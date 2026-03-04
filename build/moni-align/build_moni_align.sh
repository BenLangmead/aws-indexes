#!/bin/bash
# Build script for MONI-align on Amazon Linux 2023 (Intel-based)
# This script installs all dependencies and builds MONI-align from source
# Assumes starting from a clean Amazon Linux 2023 system with no packages installed
#
# Usage:
#   ./build_moni_align.sh [S3_URL]
#
#   S3_URL (optional): S3 URL where binaries will be uploaded (e.g., s3://my-bucket/moni-align/)
#                      If provided, all binaries, libraries, and scripts will be packaged and uploaded
#
# Requirements:
#   - Must be run from the MONI-align repository root directory
#   - Requires sudo privileges for package installation
#   - Requires internet connection for downloading packages and submodules
#   - If S3_URL is provided, requires AWS CLI and appropriate IAM permissions
#
# The script will:
#   1. Install all system dependencies (gcc, cmake, development libraries, etc.)
#   2. Initialize git submodules
#   3. Build MONI-align binaries (takes 10-30+ minutes)
#   4. Verify the build was successful
#   5. (If S3_URL provided) Package and upload all binaries to S3
#
# Output binaries will be in: ./build/bin/ or ./build/

set -e  # Exit on any error

# Parse S3 URL argument
S3_URL="${1:-}"
if [ -n "$S3_URL" ]; then
    # Ensure S3 URL ends with /
    if [[ ! "$S3_URL" =~ /$ ]]; then
        S3_URL="${S3_URL}/"
    fi
    echo "S3 upload enabled. Binaries will be uploaded to: $S3_URL"
fi

echo "=========================================="
echo "MONI-align Build Script for Amazon Linux 2023"
echo "=========================================="
echo ""

# Function to check cmake version
check_cmake_version() {
    if command -v cmake >/dev/null 2>&1; then
        CMAKE_VERSION=$(cmake --version | head -n1 | sed 's/.*version \([0-9.]*\).*/\1/')
        CMAKE_MAJOR=$(echo $CMAKE_VERSION | cut -d. -f1)
        CMAKE_MINOR=$(echo $CMAKE_VERSION | cut -d. -f2)
        if [ "$CMAKE_MAJOR" -gt 3 ] || ([ "$CMAKE_MAJOR" -eq 3 ] && [ "$CMAKE_MINOR" -ge 15 ]); then
            return 0
        fi
    fi
    return 1
}

echo "Step 1: Installing system dependencies..."
echo "----------------------------------------"

# Update package manager
sudo yum update -y

# Install build tools and dependencies
sudo yum groupinstall -y "Development Tools"
PACKAGES="zlib-devel bzip2-devel xz-devel libcurl-devel openssl-devel ncurses-devel git cmake python3 bzip2 autoconf automake wget"

# Add AWS CLI if S3 upload is requested
if [ -n "$S3_URL" ]; then
    if ! command -v aws >/dev/null 2>&1; then
        echo "AWS CLI not found. Installing..."
        PACKAGES="$PACKAGES aws-cli"
    fi
fi

sudo yum install -y $PACKAGES

echo ""
echo "Step 2: Verifying CMake version..."
echo "----------------------------------------"

if check_cmake_version; then
    echo "CMake $(cmake --version | head -n1) meets requirements (>= 3.15)."
else
    echo "ERROR: CMake 3.15+ is required but not found or version is too old."
    echo "Please install CMake 3.15 or newer."
    exit 1
fi

echo "Step 2.5 cloning"
if [[ ! -f moni-align/CMakeLists.txt ]] ; then
    git clone https://github.com/BenLangmead/moni-align
fi

cd moni-align

echo ""
echo "Step 3: Verifying we're in the MONI-align repository..."
echo "----------------------------------------"

if [ ! -f "CMakeLists.txt" ]; then
    echo "ERROR: CMakeLists.txt not found. Please run this script from the MONI-align repository root."
    exit 1
fi

echo "Current directory: $(pwd)"
echo "Repository root confirmed."

echo ""
echo "Step 4: Initializing git submodules..."
echo "----------------------------------------"

if [ -f ".gitmodules" ]; then
    if [ -d "thirdparty/sdsl-lite/.git" ]; then
        echo "Git submodules appear to be already initialized."
    else
        echo "Initializing git submodules (this may take a while)..."
        git submodule update --init --recursive
        echo "Git submodules initialized successfully."
    fi
else
    echo "WARNING: .gitmodules not found. Skipping submodule initialization."
fi

echo ""
echo "Step 5: Creating build directory..."
echo "----------------------------------------"

if [ -d "build" ]; then
    echo "Build directory already exists. Cleaning it..."
    rm -rf build
fi
mkdir -p build
cd build

echo ""
echo "Step 6: Configuring with CMake..."
echo "----------------------------------------"

cmake .. -DCMAKE_BUILD_TYPE=Release

echo ""
echo "Step 7: Building MONI-align..."
echo "----------------------------------------"
echo "WARNING: This will take a significant amount of time (10-30+ minutes)"
echo "DO NOT use make -j as there are implicit dependencies between subprojects"
echo ""

make

echo ""
echo "Step 8: Verifying build..."
echo "----------------------------------------"

MONI_EXECUTABLE=""
if [ -f "moni" ]; then
    MONI_EXECUTABLE="$(pwd)/moni"
elif [ -f "bin/moni" ]; then
    MONI_EXECUTABLE="$(pwd)/bin/moni"
else
    echo "ERROR: moni executable not found in expected locations!"
    echo "Build may have failed. Check the output above for errors."
    exit 1
fi

echo "=== Build successful! ==="
echo ""
echo "MONI-align binaries have been built successfully."
echo "Main executable location: $MONI_EXECUTABLE"
echo ""

if [ -d "bin" ]; then
    echo "Other built executables:"
    ls -lh bin/ | grep -v "^total" | awk '{print "  " $9 " (" $5 ")"}'
fi

cd ..

# Step 9: Package and upload to S3 if requested
if [ -n "$S3_URL" ]; then
    echo ""
    echo "Step 9: Packaging and uploading to S3..."
    echo "----------------------------------------"
    
    # Verify AWS CLI is available
    if ! command -v aws >/dev/null 2>&1; then
        echo "ERROR: AWS CLI is required for S3 upload but not found."
        exit 1
    fi
    
    # Create temporary directory for packaging
    PACKAGE_DIR=$(mktemp -d)
    PACKAGE_NAME="moni-align-binaries"
    PACKAGE_PATH="$PACKAGE_DIR/$PACKAGE_NAME"
    
    echo "Creating package directory: $PACKAGE_PATH"
    mkdir -p "$PACKAGE_PATH/bin"
    mkdir -p "$PACKAGE_PATH/lib"
    
    # Copy all executables from build/bin/
    if [ -d "build/bin" ]; then
        echo "Copying executables from build/bin/..."
        cp -r build/bin/* "$PACKAGE_PATH/bin/" 2>/dev/null || true
    fi
    
    # Also check for executables directly in build/ directory (but not scripts)
    echo "Finding additional executables in build directory..."
    find build -maxdepth 1 -type f -executable ! -name "*.sh" -exec cp {} "$PACKAGE_PATH/bin/" \; 2>/dev/null || true
    
    # Copy moni script (Python wrapper) - check multiple locations
    MONI_FOUND=false
    if [ -f "build/moni" ]; then
        echo "Copying moni script from build/..."
        cp build/moni "$PACKAGE_PATH/bin/moni"
        MONI_FOUND=true
    elif [ -f "build/bin/moni" ]; then
        echo "Copying moni script from build/bin/..."
        cp build/bin/moni "$PACKAGE_PATH/bin/moni"
        MONI_FOUND=true
    fi
    
    if [ "$MONI_FOUND" = false ]; then
        echo "WARNING: moni script not found in expected locations!"
    fi
    
    # Make sure all files in bin are executable (including the Python moni script)
    find "$PACKAGE_PATH/bin" -type f -exec chmod +x {} \;
    
    echo "Binaries packaged:"
    ls -lh "$PACKAGE_PATH/bin/" | tail -n +2 | awk '{print "  " $9 " (" $5 ")"}'
    
    # Copy all libraries from build/lib/
    if [ -d "build/lib" ]; then
        echo "Copying libraries from build/lib/..."
        # Copy .so, .a files and any other library files
        find build/lib -type f \( -name "*.so" -o -name "*.so.*" -o -name "*.a" \) -exec cp {} "$PACKAGE_PATH/lib/" \;
    fi
    
    # Create a README with installation instructions
    cat > "$PACKAGE_PATH/README.txt" <<EOF
MONI-align Binary Distribution
==============================

This package contains all MONI-align binaries, libraries, and scripts needed to run
MONI-align on Amazon Linux 2023 (Intel-based).

Installation:
-------------
1. Extract this package to a directory (e.g., /opt/moni-align or ~/moni-align)
2. Add the bin directory to your PATH:
   export PATH=\$PATH:/path/to/moni-align/bin
3. Set LD_LIBRARY_PATH to include the lib directory:
   export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:/path/to/moni-align/lib

Usage:
------
After installation, you can use the 'moni' command:

  Index building:  moni build -h
  Alignment:       moni align -h

Example index build:
  moni build -f <reference.fasta.gz> -o <output_prefix>

Example alignment:
  moni align -i <index_prefix> -1 <mate1.fastq> -2 <mate2.fastq> -o <output.sam>

System Requirements:
-------------------
- Amazon Linux 2023 (Intel-based)
- Python 3 (for the moni wrapper script)
- Standard system libraries (zlib, bzip2, xz, curl, openssl, ncurses)

Note: The binaries are statically linked where possible, but some system libraries
may still be required. If you encounter missing library errors, install the
corresponding -devel packages on your system.

Contents:
---------
- bin/    : All executable binaries and the moni wrapper script
- lib/    : Shared and static libraries required by the binaries
EOF
    
    # Create an installation script
    cat > "$PACKAGE_PATH/install.sh" <<'INSTALL_EOF'
#!/bin/bash
# Installation script for MONI-align binaries

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${1:-$HOME/moni-align}"

echo "Installing MONI-align binaries to: $INSTALL_DIR"

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy files
echo "Copying files..."
cp -r "$SCRIPT_DIR/bin" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/lib" "$INSTALL_DIR/"

# Set permissions
chmod +x "$INSTALL_DIR/bin"/*

echo ""
echo "Installation complete!"
echo ""
echo "To use MONI-align, add to your ~/.bashrc or ~/.bash_profile:"
echo "  export PATH=\$PATH:$INSTALL_DIR/bin"
echo "  export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$INSTALL_DIR/lib"
echo ""
echo "Or run:"
echo "  source <(echo 'export PATH=\$PATH:$INSTALL_DIR/bin; export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$INSTALL_DIR/lib')"
echo ""
INSTALL_EOF
    chmod +x "$PACKAGE_PATH/install.sh"
    
    # Create a download script for easy retrieval
    cat > "$PACKAGE_PATH/download.sh" <<DOWNLOAD_EOF
#!/bin/bash
# Download script for MONI-align binaries from S3
# Usage: ./download.sh [INSTALL_DIR]

set -e

S3_URL="$S3_URL"
INSTALL_DIR="\${1:-\$HOME/moni-align}"

echo "Downloading MONI-align binaries from S3..."
echo "S3 URL: \$S3_URL"
echo "Install directory: \$INSTALL_DIR"

# Check if AWS CLI is available
if ! command -v aws >/dev/null 2>&1; then
    echo "ERROR: AWS CLI is required but not found."
    echo "Please install AWS CLI: sudo yum install -y aws-cli"
    exit 1
fi

# Create temporary directory
TMP_DIR=\$(mktemp -d)
trap "rm -rf \$TMP_DIR" EXIT

# Download tarball from S3
TARBALL_NAME="moni-align-binaries.tar.gz"
echo "Downloading tarball..."
aws s3 cp "\${S3_URL}\${TARBALL_NAME}" "\$TMP_DIR/\${TARBALL_NAME}"

# Extract tarball
echo "Extracting..."
cd "\$TMP_DIR"
tar -xzf "\${TARBALL_NAME}"

# Run installation
if [ -f "\$TMP_DIR/moni-align-binaries/install.sh" ]; then
    "\$TMP_DIR/moni-align-binaries/install.sh" "\$INSTALL_DIR"
else
    echo "ERROR: install.sh not found in package"
    exit 1
fi

echo ""
echo "Download and installation complete!"
DOWNLOAD_EOF
    chmod +x "$PACKAGE_PATH/download.sh"
    
    # Create a tarball for easier distribution
    echo "Creating tarball..."
    cd "$PACKAGE_DIR"
    tar -czf "${PACKAGE_NAME}.tar.gz" "$PACKAGE_NAME"
    
    # Upload to S3
    echo "Uploading to S3: $S3_URL"
    aws s3 cp "${PACKAGE_NAME}.tar.gz" "${S3_URL}${PACKAGE_NAME}.tar.gz"
    
    # Also upload individual files for easier access
    echo "Uploading individual files..."
    aws s3 sync "$PACKAGE_NAME/" "${S3_URL}" --exclude "*.txt" --exclude "*.sh"
    aws s3 cp "$PACKAGE_NAME/README.txt" "${S3_URL}README.txt"
    aws s3 cp "$PACKAGE_NAME/install.sh" "${S3_URL}install.sh"
    aws s3 cp "$PACKAGE_NAME/download.sh" "${S3_URL}download.sh"
    
    # Return to original directory
    cd - > /dev/null
    
    # Cleanup
    rm -rf "$PACKAGE_DIR"
    
    echo ""
    echo "=== Upload complete! ==="
    echo ""
    echo "Files uploaded to: $S3_URL"
    echo ""
    echo "To download and install on another machine:"
    echo "  1. Download the install script:"
    echo "     aws s3 cp ${S3_URL}install.sh ./install.sh"
    echo "  2. Download the tarball:"
    echo "     aws s3 cp ${S3_URL}${PACKAGE_NAME}.tar.gz ./"
    echo "  3. Extract and run install.sh:"
    echo "     tar -xzf ${PACKAGE_NAME}.tar.gz"
    echo "     cd $PACKAGE_NAME && ./install.sh [INSTALL_DIR]"
    echo ""
    echo "Or use the download script:"
    echo "  aws s3 cp ${S3_URL}download.sh ./download.sh"
    echo "  chmod +x download.sh"
    echo "  ./download.sh [INSTALL_DIR]"
    echo ""
fi

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""
echo "To use MONI-align:"
echo "  Index building:  ./build/moni build -h"
echo "  Alignment:       ./build/moni align -h"
echo ""
echo "Example index build:"
echo "  ./build/moni build -f <reference.fasta.gz> -o <output_prefix>"
echo ""
echo "Example alignment:"
echo "  ./build/moni align -i <index_prefix> -1 <mate1.fastq> -2 <mate2.fastq> -o <output.sam>"
echo ""
