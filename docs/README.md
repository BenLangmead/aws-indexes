# docs — GitHub Pages site

Public catalog of genome index HTTPS and S3 URLs (`https://benlangmead.github.io/aws-indexes/`).

## Local preview

Requires **Ruby 3.0 or newer** and Bundler. (Ruby 2.x is too old for current `github-pages` / native gem builds.) A `.ruby-version` file is provided for rbenv/asdf/chruby.

The `github-pages` gem forces **safe mode** locally, so custom `_plugins` do not run. On **Ruby 3.2+**, Liquid 4.0.3 still calls removed `Object#tainted?`, so use the wrapper (or `RUBYOPT`) below:

```bash
cd docs
bundle install
./jekyll-local.sh serve
```

Equivalent without the script:

```bash
export RUBYOPT="-r$(pwd)/.jekyll-bootstrap.rb${RUBYOPT:+ ${RUBYOPT}}"
bundle exec jekyll serve
```

**Ruby 3.4+** (including **Ruby 4.x**): the Gemfile adds `csv`, `bigdecimal`, and `webrick` (for `jekyll serve`), which are no longer default gems.

Open <http://localhost:4000/aws-indexes/> when using a project site `baseurl` (GitHub sets this automatically on Pages). For a root URL locally, add to `_config.yml` temporarily:

```yaml
url: "http://localhost:4000"
baseurl: ""
```

Or pass flags:

```bash
./jekyll-local.sh serve --baseurl ""
```

## Analytics (Google Analytics 4)

The site supports **GA4** via the `google_analytics` key in [`_config.yml`](_config.yml) (Google tag / `gtag.js`). Until you set it, no analytics scripts are included.

1. In [Google Analytics](https://analytics.google.com/), create a **GA4** property and a **Web** data stream for your Pages URL (e.g. `https://benlangmead.github.io/aws-indexes/`).
2. Copy the **Measurement ID** (`G-XXXXXXXXXX`).
3. Add to `_config.yml`:
   ```yaml
   google_analytics: G-XXXXXXXXXX
   ```
4. Push to GitHub; Pages will rebuild. Reports appear under **Reports** and **Realtime** in GA4.

**Outbound links:** [`assets/js/ga-outbound.js`](assets/js/ga-outbound.js) sends an `outbound_click` event when visitors follow links to another hostname (S3, GitHub, external docs). You can mark this event as a **key event** in GA4 if you want it in summaries.

**Local preview:** Copy [`_config_local.yml.example`](_config_local.yml.example) to `_config_local.yml`, set `google_analytics` there, and run:

```bash
bundle exec jekyll serve --config _config.yml,_config_local.yml
```

(`_config_local.yml` is gitignored.)

**Privacy:** [`privacy.md`](privacy.md) describes GA4 usage; the footer links to it on every page.

## Checks

- [`check_k2_links.py`](check_k2_links.py) — verify `https://` URLs in `k2.md` only (run from repo root or pass path to `k2.md`).
- [`check_site_links.py`](check_site_links.py) — scan all local site sources (`*.md` under `docs/`, excluding `_site/` and by default `skills/`), plus `_layouts/*.html`; checks internal paths and remote HTTP(S) links. Options include `--check-s3`, `--check-ftp`, `--include-skills`, `--no-network`, `--request-delay` (spacing between requests to reduce throttling), `--timeout`, `--workers`. Some hosts may still return errors to automated clients. Example: `python3 docs/check_site_links.py --root docs`.

## Layouts

- **`default`**: sidebar navigation + main content (most Markdown pages).
- **`full`**: full-width main only; use front matter `layout: full` when needed.
