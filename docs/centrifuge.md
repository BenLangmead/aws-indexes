# Centrifuge indexes

Centrifuge is a very rapid and memory-efficient system for the classification of DNA sequences from microbial samples.

<div class="datatable-begin"></div>

Collection                                           | Date            | Size    | HTTPS URL                        | S3 URL
---------------------------------------------------- | --------------- | ------- | -------------------------------- | -------
Refseq: bacteria, archaea, viral, human (compressed) |  December, 2016 | 5.4 GB  | [.tar.gz][cent_bavm_comp]        | [.tar.gz][cent_bavm_comp_s3]
Refseq: bacteria, archaea, viral, human              |  December, 2016 | 7.9 GB  | [.tar.gz][cent_bavm]             | [.tar.gz][cent_bavm_s3]
Refseq: bacteria, archaea (compressed)               |  April, 2018    | 64 GB   | [.tar.gz][cent_ba_comp]          | [.tar.gz][cent_ba_comp_s3]
NCBI: nucleotide non-redundant sequences             |  March, 2018    | 6.3 GB  | [.tar.gz][cent_nt]               | [.tar.gz][cent_nt_s3]

<div class="datatable-end"></div>

[cent_bavm_comp]: https://genome-idx.s3.amazonaws.com/centrifuge/p_compressed%2Bh%2Bv.tar.gz
[cent_bavm_comp_s3]: s3://genome-idx/centrifuge/p_compressed%2Bh%2Bv.tar.gz

[cent_bavm]: https://genome-idx.s3.amazonaws.com/centrifuge/p%2Bh%2Bv.tar.gz
[cent_bavm_s3]: s3://genome-idx/centrifuge/p%2Bh%2Bv.tar.gz

[cent_ba_comp]: https://genome-idx.s3.amazonaws.com/centrifuge/p_compressed_2018_4_15.tar.gz
[cent_ba_comp_s3]: s3://genome-idx/centrifuge/p_compressed_2018_4_15.tar.gz

[cent_nt]: https://genome-idx.s3.amazonaws.com/centrifuge/nt_2018_3_3.tar.gz
[cent_nt_s3]: s3://genome-idx/centrifuge/nt_2018_3_3.tar.gz
