# Movi indexes

Movi ([GitHub repo](https://github.com/mohsenzakeri/Movi)) is an efficient and scalable approach for indexing and querying pangenomes.  It uses the [move structure](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2021.101) of Nishimoto and Tabei as its core, cache-efficient index structure.

The indexes below are **separator-aware, reverse-complement-aware pangenome indexes** for **Movi 2**.  They are built in Movi's `regular-thresholds` mode (mode 6) and include **threshold** information, so they support the full range of Movi 2 queries: pseudo-matching lengths (`--pml`), Ziv–Lempel matching lengths (`--zml`), `--count`, *k*-mer presence/counts (`--kmer`), maximal exact matches (`--mem`), and — using the shipped null model — read `--classify` and `--filter`.  A `%` separator is placed after every record and between each record's forward and reverse-complement copy, so matches never spuriously extend across a record (contig) boundary.

Each index was built on JHU's Rockfish cluster.  The two larger indexes (HPRC Release 2 and OpenHGL) are the first Movi indexes whose reference length exceeds 2<sup>40</sup> bp; they use a wide (6-byte) threshold format produced by an updated build path.  **The published indexes are queryable by stock Movi 2** — the wide-threshold change is build-time only and does not alter the on-disk index format.

Every index ships a signed **`test-witness.json`** recording the results of a corner-case query-mode test suite (separator non-extension, reverse-complement symmetry, illegal/non-ACGT character handling, positive-vs-null separation, and cross-mode consistency) run against that exact `index.movi`; the witness pins the index's SHA-256 and the Movi commit, and carries a self-verifying `self_sha256`.  All three indexes passed with zero failures.

*The following table lists each complete `.tar.gz` archive, then the individual component files contained in that archive.*

<div class="datatable-begin"></div>

Index / file | Size | HTTPS
--- | ---:| ---
**HPRC Release 1 (Year 1), 95 human haplotypes** (complete `.tar.gz`) | 18.9 GB | [.tar.gz][yr1_tgz]
*Link above is recommended; links below are its individual components* | |
`index.movi` | 37.6 GB | [.movi][yr1_movi]
`ftab.2.bin` | 528 B | [.bin][yr1_ftab2]
`ftab.4.bin` | 8.2 KB | [.bin][yr1_ftab4]
`ftab.6.bin` | 131 KB | [.bin][yr1_ftab6]
`ftab.8.bin` | 2.1 MB | [.bin][yr1_ftab8]
`ftab.10.bin` | 33.6 MB | [.bin][yr1_ftab10]
`ftab.12.bin` | 537 MB | [.bin][yr1_ftab12]
`movi.pml.nulldb` | 1.2 MB | [.nulldb][yr1_pml]
`movi.zml.nulldb` | 1.2 MB | [.nulldb][yr1_zml]
`null_reads.fasta` | 161 KB | [.fasta][yr1_null]
`test-witness.json` | 10 KB | [.json][yr1_wit]
`movi-index.yaml` | 1.1 KB | [.yaml][yr1_yaml]
`hprc-yr1.seqdict.json` | 4.9 MB | [.json][yr1_seq]
**HPRC Release 2 (Year 2), 472 human haplotypes** (complete `.tar.gz`) | 26.1 GB | [.tar.gz][yr2_tgz]
*Link above is recommended; links below are its individual components* | |
`index.movi` | 48.6 GB | [.movi][yr2_movi]
`ftab.2.bin` | 528 B | [.bin][yr2_ftab2]
`ftab.4.bin` | 8.2 KB | [.bin][yr2_ftab4]
`ftab.6.bin` | 131 KB | [.bin][yr2_ftab6]
`ftab.8.bin` | 2.1 MB | [.bin][yr2_ftab8]
`ftab.10.bin` | 33.6 MB | [.bin][yr2_ftab10]
`ftab.12.bin` | 537 MB | [.bin][yr2_ftab12]
`movi.pml.nulldb` | 1.2 MB | [.nulldb][yr2_pml]
`movi.zml.nulldb` | 1.2 MB | [.nulldb][yr2_zml]
`null_reads.fasta` | 161 KB | [.fasta][yr2_null]
`test-witness.json` | 10 KB | [.json][yr2_wit]
`movi-index.yaml` | 1.1 KB | [.yaml][yr2_yaml]
`hprc-yr2.seqdict.json` | 5.0 MB | [.json][yr2_seq]
**OpenHGL, 579 human haplotypes** (complete `.tar.gz`) | 28.1 GB | [.tar.gz][ohgl_tgz]
*Link above is recommended; links below are its individual components* | |
`index.movi` | 51.6 GB | [.movi][ohgl_movi]
`ftab.2.bin` | 528 B | [.bin][ohgl_ftab2]
`ftab.4.bin` | 8.2 KB | [.bin][ohgl_ftab4]
`ftab.6.bin` | 131 KB | [.bin][ohgl_ftab6]
`ftab.8.bin` | 2.1 MB | [.bin][ohgl_ftab8]
`ftab.10.bin` | 33.6 MB | [.bin][ohgl_ftab10]
`ftab.12.bin` | 537 MB | [.bin][ohgl_ftab12]
`movi.pml.nulldb` | 1.2 MB | [.nulldb][ohgl_pml]
`movi.zml.nulldb` | 1.2 MB | [.nulldb][ohgl_zml]
`null_reads.fasta` | 161 KB | [.fasta][ohgl_null]
`test-witness.json` | 10 KB | [.json][ohgl_wit]
`movi-index.yaml` | 1.1 KB | [.yaml][ohgl_yaml]
`openhgl.seqdict.json` | 6.4 MB | [.json][ohgl_seq]

<div class="datatable-end"></div>

The `.seqdict.json` file maps each index position back to its source record (sample, contig, and orientation).  The `movi-index.yaml` sidecar records the index header (mode, reference length, run count) and build provenance.

Corresponding S3 URLs can be obtained by replacing the `https://genome-idx.s3.amazonaws.com/` prefix with `s3://genome-idx/`.

Movi is the work of Mohsen Zakeri, Nathaniel Brown, Travis Gagie and Ben Langmead.

[yr1_tgz]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/hprc-yr1.tar.gz
[yr1_movi]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/index.movi
[yr1_ftab2]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.2.bin
[yr1_ftab4]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.4.bin
[yr1_ftab6]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.6.bin
[yr1_ftab8]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.8.bin
[yr1_ftab10]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.10.bin
[yr1_ftab12]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/ftab.12.bin
[yr1_pml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/movi.pml.nulldb
[yr1_zml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/movi.zml.nulldb
[yr1_null]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/null_reads.fasta
[yr1_wit]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/test-witness.json
[yr1_yaml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/index/movi-index.yaml
[yr1_seq]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr1/hprc-yr1.seqdict.json
[yr2_tgz]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/hprc-yr2.tar.gz
[yr2_movi]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/index.movi
[yr2_ftab2]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.2.bin
[yr2_ftab4]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.4.bin
[yr2_ftab6]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.6.bin
[yr2_ftab8]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.8.bin
[yr2_ftab10]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.10.bin
[yr2_ftab12]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/ftab.12.bin
[yr2_pml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/movi.pml.nulldb
[yr2_zml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/movi.zml.nulldb
[yr2_null]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/null_reads.fasta
[yr2_wit]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/test-witness.json
[yr2_yaml]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/index/movi-index.yaml
[yr2_seq]: https://genome-idx.s3.amazonaws.com/movi/hprc-yr2/hprc-yr2.seqdict.json
[ohgl_tgz]: https://genome-idx.s3.amazonaws.com/movi/openhgl/openhgl.tar.gz
[ohgl_movi]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/index.movi
[ohgl_ftab2]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.2.bin
[ohgl_ftab4]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.4.bin
[ohgl_ftab6]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.6.bin
[ohgl_ftab8]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.8.bin
[ohgl_ftab10]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.10.bin
[ohgl_ftab12]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/ftab.12.bin
[ohgl_pml]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/movi.pml.nulldb
[ohgl_zml]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/movi.zml.nulldb
[ohgl_null]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/null_reads.fasta
[ohgl_wit]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/test-witness.json
[ohgl_yaml]: https://genome-idx.s3.amazonaws.com/movi/openhgl/index/movi-index.yaml
[ohgl_seq]: https://genome-idx.s3.amazonaws.com/movi/openhgl/openhgl.seqdict.json
