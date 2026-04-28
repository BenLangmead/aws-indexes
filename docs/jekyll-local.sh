#!/usr/bin/env bash
# Run Jekyll with a bootstrap that fixes Liquid 4.0.3 + Ruby 3.2+ when using the
# github-pages gem (which forces safe mode, so _plugins never load locally).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export RUBYOPT="-r${ROOT}/.jekyll-bootstrap.rb${RUBYOPT:+ ${RUBYOPT}}"
cd "$ROOT"
exec bundle exec jekyll "$@"
