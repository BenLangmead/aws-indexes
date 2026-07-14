# Mumemto and Shredtools HPRC indexes

Mumemto ([GitHub repo](https://github.com/vikshiv/mumemto)) is an efficient multi-MUM finder for large pangenomes.  Multi-MUMs have a variety of uses, including forming a pangenome coordinate system, visualizing synteny, and serving as a basis for multiple genome alignment.

Shredtools ([GitHub repo](https://github.com/vikshiv/shredtools)) is a companion tool that operates over multi-MUMs to navigate the pangenome coordinate system.  Shredtools can extract homologous regions across a pangenome using multi-MUMs as a framework for the underlying multiple alignment.

We provide pre-computed multi-MUMs for a collection of 476 high-quality human genome assemblies (available from [https://github.com/lh3/OpenHGL](https://github.com/lh3/OpenHGL)).  The formats are as follows:

1. `*.bumbl` - native binary format for Mumemto.  Fast loading into memory for downstream applications (Mumemto python API available), and can stream to human-readable `*.mums` with `mumemto convert`.

    > **Note:** `*.bumbl` files are indexable with a `*.bumbl.bi` file (introduced with Shredtools).  This enables retrieving the subset of multi-MUMs contained in a requested region from any assembly in the collection.

2. `*.mums.gz` - gzip of human readable `*.mums` file, sorted by occurrence in the first genome (CHM13).
3. `*.lengths` - a manifest of contig lengths for each genome, used in multiple downstream Mumemto scripts, and dictates the order of genomes / contigs in the MUM file.
4. `hprcv2.athresh` - threshold file necessary to merge in new genomes to the pangenome collection.

The following files contain strict multi-MUMs, exact matches that appear in every genome, exactly once per assembly.  This is useful for building alignments, graphs, and identifying variation.

Corresponding S3 URLs can be obtained by replacing the `https://genome-idx.s3.amazonaws.com/` prefix with `s3://genome-idx/`.

> **Note:** `hprcv2.lengths` can be used with any of the mums/bumbl files, since it contains a manifest of assembly and contig lengths in the collection.  `hprcv2.athresh` can also be used to merge in new assemblies, if mumemto was run between the CHM13 and the new assembly.

<div class="datatable-begin"></div>

File name | Description | HTTPS URLs
--- | --- | ---
`hprcv2.*` | All multi-MUMs in HPRCv2, the raw output of running Mumemto.  Suitable if you need strict multi-MUMs for methods development. | [.athresh (5.9 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.athresh), [.bumbl (71 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.bumbl), [.bumbl.bi (53 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.bumbl.bi), [.bumbl.gz (28 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.bumbl.gz), [.lengths (3.6 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.lengths), [.mums.gz (36 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2.mums.gz)
`hprcv2_filt.*` | Filtered output, only including "collinear" multi-MUMs (only 0.01% matches filtered).  Suitable for most use cases. | [.bumbl (71 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_filt.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_filt.bumbl.bi), [.bumbl.gz (28 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_filt.bumbl.gz), [.mums.gz (36 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_filt.mums.gz)
`hprcv2_enhanced_filt.*` | Includes additional "local" multi-MUMs, not globally unique, but unique in a local region between global multi-MUMs.  Forms the "pangenome coordinate system".  Best for use with Shredtools. | [.bumbl (82 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_filt.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_filt.bumbl.bi), [.bumbl.gz (32 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_filt.bumbl.gz), [.mums.gz (41 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_filt.mums.gz)

<div class="datatable-end"></div>

In the following files, we merge consecutive multi-MUMs separated by an SNV.  Lines in these files may contain single base mismatches, but no indels.  This is useful for identifying pangenome coordinates and syntenic blocks with fewer (but longer) match blocks.  These files were generated post-filtering out non-collinear matches.

<div class="datatable-begin"></div>

File name | Description | HTTPS URLs
--- | --- | ---
`hprcv2_merged.*` | Collinear multi-MUMs, merged if separated by only a SNV | [.bumbl (26 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_merged.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_merged.bumbl.bi), [.bumbl.gz (12 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_merged.bumbl.gz), [.mums.gz (14 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_merged.mums.gz)
`hprcv2_enhanced_merged.*` | Collinear multi-MUMs and "local" multi-MUMs, merged if separated by only a SNV | [.bumbl (30 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_merged.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_merged.bumbl.bi), [.bumbl.gz (13 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_merged.bumbl.gz), [.mums.gz (16 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprc/hprcv2_enhanced_merged.mums.gz)

<div class="datatable-end"></div>

## Shredtools HPRC indexes

Shredtools uses multi-MUMs to slice and extract homologous regions.  See the interactive webapp version at [https://vikshiv.github.io/shredtools/](https://vikshiv.github.io/shredtools/), which uses the following files:

<div class="datatable-begin"></div>

File name | Description | HTTPS URLs
--- | --- | ---
`hprcv2_enhanced_merged.*` | HPRCv2 multi-MUM coordinate system.  Recommended preset for most Shredtools analyses. | [.bumbl (30 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_enhanced_merged.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_enhanced_merged.bumbl.bi), [.lengths (3.6 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_enhanced_merged.lengths)
`hprcv2_merged.*` | HPRCv2 coordinate system with only strict multi-MUMs (lower coverage than enhanced version). | [.bumbl (26 GB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_merged.bumbl), [.bumbl.bi (52 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_merged.bumbl.bi), [.lengths (3.6 MB)](https://genome-idx.s3.amazonaws.com/mumemto/hprcv2_merged.lengths)
`hprcv1.*` | Original HPRCv1 pangenome coordinate system. | [.bumbl](https://genome-idx.s3.amazonaws.com/mumemto/hprcv1.bumbl), [.bumbl.bi](https://genome-idx.s3.amazonaws.com/mumemto/hprcv1.bumbl.bi), [.lengths](https://genome-idx.s3.amazonaws.com/mumemto/hprcv1.lengths)

<div class="datatable-end"></div>

> **Note:** FASTA sequences are not hosted alongside these index files.  Shredtools retrieves genome sequences directly from the HPRC assembly collection (`s3://human-pangenomics/`).  The interactive webapp version can also fetch queried sequences from the HPRC S3 bucket.

Mumemto and Shredtools are the work of Vikram Shivakumar and Ben Langmead.
