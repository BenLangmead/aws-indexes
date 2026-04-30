# Movi indexes

Movi ([GitHub repo](https://github.com/mohsenzakeri/Movi)) is an efficient and scalable approach for indexing and querying pangenomes.  It uses the [move structure](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ICALP.2021.101) of Nishimoto and Tabei as its core, cache-efficient index structure.

Indexes below are compatible with **Movi 2**. They include **threshold** information and are intended for use with Movi's default `regular-thresholds` mode.

*The following table lists each complete `.tar.gz` archive, then the individual component files contained in that archive.*

<div class="datatable-begin"></div>

Index / file | Size | HTTPS
--- | ---:| ---
HPRC Release 2, 466 human haplotypes (complete `.tar.gz`) | 25.8 GB | [.tar.gz][movi_hprc2_tgz_http]
*Link above is recommended; links below are its individual components* | |
`build.log` | 3.4 KB | [.log][movi_hprc2_log_http]
`index.movi` | 48.4 GB | [.movi][movi_hprc2_movi_http]
`movi.pml.nulldb` | 1.1 MB | [.pml.nulldb][movi_hprc2_pml_http]
`movi.zml.nulldb` | 1.1 MB | [.zml.nulldb][movi_hprc2_zml_http]
`null_reads.fasta` | 157 KB | [.fasta][movi_hprc2_fasta_http]
`ref.list` | 17 KB | [.list][movi_hprc2_list_http]
HPRC Release 1, 96 human haplotypes (complete `.tar.gz`) | 18.8 GB | [.tar.gz][movi_hprc1_tgz_http]
*Link above is recommended; links below are its individual components* | |
`CMakeLists.txt` | 3.2 KB | [.txt][movi_hprc1_cmake_http]
`build.log` | 10.1 KB | [.log][movi_hprc1_log_http]
`index.html` | 141 B | [.html][movi_hprc1_html_http]
`index.movi` | 37.7 GB | [.movi][movi_hprc1_movi_http]
`movi.pml.nulldb` | 1.1 MB | [.pml.nulldb][movi_hprc1_pml_http]
`movi.zml.nulldb` | 1.1 MB | [.zml.nulldb][movi_hprc1_zml_http]
`null_reads.fasta` | 157 KB | [.fasta][movi_hprc1_fasta_http]
`reference_names` | 1.2 KB | [reference_names][movi_hprc1_refnames_http]

<div class="datatable-end"></div>

Corresponding S3 URLs can be obtained by replacing the `https://genome-idx.s3.amazonaws.com/` prefix with `s3://genome-idx/`.

Movi is the work of Mohsen Zakeri, Nathaniel Brown, Travis Gagie and Ben Langmead.

[movi_hprc2_tgz_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh.tar.gz
[movi_hprc2_log_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/build.log
[movi_hprc2_movi_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/index.movi
[movi_hprc2_pml_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/movi.pml.nulldb
[movi_hprc2_zml_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/movi.zml.nulldb
[movi_hprc2_fasta_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/null_reads.fasta
[movi_hprc2_list_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc2_thresh/ref.list
[movi_hprc1_tgz_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh.tar.gz
[movi_hprc1_cmake_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/CMakeLists.txt
[movi_hprc1_log_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/build.log
[movi_hprc1_html_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/index.html
[movi_hprc1_movi_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/index.movi
[movi_hprc1_pml_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/movi.pml.nulldb
[movi_hprc1_zml_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/movi.zml.nulldb
[movi_hprc1_fasta_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/null_reads.fasta
[movi_hprc1_refnames_http]: https://genome-idx.s3.amazonaws.com/movi/movi2_hprc1_thresh/reference_names
