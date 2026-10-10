<style>
/* These tables have long, prose descriptions.  On wider viewports, wrap the
   columns to fit the content area instead of forcing a very wide horizontal
   scroll.  On small screens they fall back to the site-wide horizontal-scroll
   behavior. */
@media (min-width: 721px) {
  .table-scroll table { width: 100%; min-width: 0; }
  .table-scroll th,
  .table-scroll td { white-space: normal; overflow-wrap: anywhere; vertical-align: top; }
  .table-scroll th:first-child,
  .table-scroll td:first-child { white-space: nowrap; }
}
</style>

# Cliffy indexes

Cliffy ([GitHub repo](https://github.com/oma219/cliffy)) is a classifier for 16S rRNA sequencing reads.  It indexes a collection of reference sequences grouped into *documents* (here, one document per taxonomic group) and, for each read, reports which documents contain its exact matches.  The index is an r-index, a compressed full-text index built from the run-length Burrows-Wheeler transform (BWT), together with *document array profiles*, which record for each BWT run how far a match can extend in each document.  Cliffy's main contribution is *cliff compression*, which uses the taxonomy to shrink these profiles to a small, fixed number of columns.  Because the compressed profiles keep only part of the per-document information, a read's listing can omit its source document or name a taxonomically nearby one instead.

The two indexes below cover the SILVA 138.1 SSURef NR99 16S/18S rRNA database at roughly genus resolution.  They differ in how the reference text is represented and in which version of Cliffy can read them.

<div class="datatable-begin"></div>

Index | Documents | Text | Query with | Download
--- | --- | --- | --- | ---
**SILVA 138.1 genera, minimizer-digested** (2025) | 9,118 genera, 402,378 sequences | DNA, minimizer-digested (k=4, w=11), with reverse complements | cliffy v2.0.0 | [.tar.gz (1.2 GB)][gen_tgz], [.md5][gen_md5], [doc_to_taxon.tsv (2.1 MB)][gen_tsv], [README.md][gen_readme]
**SILVA 138.1 taxonomic groups, full text** (2023) | 8,633 groups, 358,428 sequences | RNA alphabet (U), full text, forward strand only | cliffy commit [99cc40e][c99] | [.tar.gz (1.1 GB)][tax_tgz], [.md5][tax_md5], [doc_to_taxon.tsv (1.0 MB)][tax_tsv], [README.md][tax_readme]

<div class="datatable-end"></div>

Corresponding S3 URLs can be obtained by replacing the `https://genome-idx.s3.amazonaws.com/` prefix with `s3://genome-idx/`.

Each archive unpacks to a directory holding `index/output.fna*` (the index files; pass `-r <dir>/index/output` to Cliffy), `doc_to_taxon.tsv`, the build `filelist.txt` mapping each input FASTA to its document ID, the build log, a `README.md` and `md5sums.txt`.  In `doc_to_taxon.tsv`, `common_lineage` is the longest SILVA lineage shared by every sequence in the document, and `common_rank_depth` is its number of fields.

> **Note:** Document IDs in Cliffy's `.listings` output are 0-based, while `doc_to_taxon.tsv` and `filelist.txt` number documents from 1.  Listing ID *d* refers to `doc_id` *d*+1.

## SILVA 138.1 genera, minimizer-digested (2025)

This index has one document per SILVA genus: 9,118 genera.  It reconstructs the minimizer-digested, cliff-compressed index from Experiment 1 of the Cliffy paper, built with the scripts in the [cliffy-experiments](https://github.com/oma219/cliffy-experiments) repository.  The genera were selected with `write_silva_genera.py -n 10000`, and each genus FASTA was converted from RNA to DNA with `seqtk seq -r`.  The index was then built in January 2025 with cliffy v2.0.0:

```
cliffy build --filelist filelist.txt --output index/output --revcomp \
  --minimizers --taxcomp --num-col 7 --two-pass <tmp-dir>
```

It differs from the paper's index in one parameter: the paper's rule for this index uses `--num-col 5`.  The BWT has n = 257,479,510 and r = 34,469,190 runs.  The archive includes the ftab, a k-mer lookup table that speeds up queries.  Query it with cliffy v2.0.0, repeating the build's options:

```
cliffy run -r silva138_genera_minimizer/index/output -p reads.fa -o out/prefix -t -c 7 -i -f
```

Loading the index took about 20 GB of memory.  Reads are DNA; Cliffy digests them into minimizers itself.

## SILVA 138.1 taxonomic groups, full text (2023)

This index has 8,633 documents, each a SILVA taxonomic group (nearly all at genus level), and indexes the full sequences, not minimizers.  Omar Ahmed built it in April 2023, before the cliffy-experiments workflow existed, with a development build of pfp-doc (Cliffy's earlier name) that reports version 1.0.6.  It uses a PFP window of 10, no reverse complements, and cliff compression with 7 columns.  The build took about 49 hours, and the BWT has r = 28,480,352 runs.

The reference text keeps SILVA's RNA alphabet, so **reads must be converted to RNA (T to U) before querying**.  Otherwise matches break at every T.

This index predates the on-disk format of cliffy v2.0.0, which added `.taxcomp.ofptr.*` and `.runcnt` files, so v2.0.0 cannot load it.  Build Cliffy at commit [99cc40e][c99] (April 23, 2024), the last commit before that format change, and run:

```
pfp_doc64 run -r silva138_taxgroups_fulltext/index/output -p reads_rna.fa -o out/prefix -t -c 7
```

With GCC 13 or newer, one of Cliffy's fetched dependencies (bwt2lcp) fails to compile because it lacks `#include <cstdint>`.  After running `cmake`, add that line near the top of `build/_deps/bwt2lcp-src/internal/include.hpp` and run `make` again.  Loading the index took about 15 GB of memory.

## Spot check

Before publishing, we queried each index with about 300 random 150 bp substrings of its own reference sequences, using the commands above.  Every read matched along its full length.  The listing included the read's source document for 81% of reads (237 of 291) in the 2025 index and 76% (220 of 289) in the 2023 index.  In the reads we examined individually, the documents listed instead were taxonomically close to the source, for example another genus in the same family or order.

Cliffy is the work of Omar Ahmed, Christina Boucher and Ben Langmead.  If you use these indexes, please cite: Ahmed O, Boucher C, Langmead B. Cliffy: robust 16S rRNA classification based on a compressed LCA index. *Genome Research* (2025). [doi:10.1101/gr.279846.124](https://doi.org/10.1101/gr.279846.124)

[c99]: https://github.com/oma219/cliffy/commit/99cc40e9e5e451952a45923390ff442bdaf99292
[gen_tgz]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_genera_minimizer/silva138_genera_minimizer.tar.gz
[gen_md5]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_genera_minimizer/silva138_genera_minimizer.tar.gz.md5
[gen_tsv]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_genera_minimizer/doc_to_taxon.tsv
[gen_readme]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_genera_minimizer/README.md
[tax_tgz]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_taxgroups_fulltext/silva138_taxgroups_fulltext.tar.gz
[tax_md5]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_taxgroups_fulltext/silva138_taxgroups_fulltext.tar.gz.md5
[tax_tsv]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_taxgroups_fulltext/doc_to_taxon.tsv
[tax_readme]: https://genome-idx.s3.amazonaws.com/cliffy/silva138_taxgroups_fulltext/README.md
