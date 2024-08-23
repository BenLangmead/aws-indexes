# Centrifuge indexes

Centrifuge is a very rapid and memory-efficient system for the classification of DNA sequences from microbial samples.

<div class="datatable-begin"></div>

Collection                                           | Date            | Size    | HTTPS URL                        | S3 URL
---------------------------------------------------- | --------------- | ------- | -------------------------------- | -------
Refseq: bacteria, archaea, viral, human (compressed) |  December, 2016 | 5.4 GB  | [.tar.gz][cent_bavm_comp]        | [.tar.gz][cent_bavm_comp_s3]
Refseq: bacteria, archaea, viral, human              |  December, 2016 | 7.9 GB  | [.tar.gz][cent_bavm]             | [.tar.gz][cent_bavm_s3]
Refseq: bacteria, archaea (compressed)               |  April, 2018    | 6.2 GB  | [.tar.gz][cent_ba_comp]          | [.tar.gz][cent_ba_comp_s3]
NCBI: nucleotide non-redundant sequences             |  March, 2018    | 64 GB   | [.tar.gz][cent_nt]               | [.tar.gz][cent_nt_s3]

<div class="datatable-end"></div>

Centrifuge is the work of Daehwan Kim, Li Song, Florian Breitwieser, Chanhee Park, Steven Salzberg among others.
Please see the [Centrifuge website](https://ccb.jhu.edu/software/centrifuge/) for more information on the software, authors, and how to cite it.

# nt Database from Lawrence Livermore National Laboratory

A team from Lawrence Livermore National Laboratory (LLNL) have constructed a Centrifuge database spanning all of the BLAST nt sequences.  This is described in [a recent manuscript](https://doi.org/10.1101/2024.06.12.598617).  This database can be downloaded as a collection of 7zip archives.  You will need to have the [7zip softare](https://7-zip.org/download.html) (i.e. the `7z` command) installed.  Altogether, the compressed archives occupy 284G.  These commands will download the archives:

```
curl https://genome-idx.s3.amazonaws.com/centrifuge/llnl/nt_wntr23/nt_wntr23_filt.cf.7z.[001-071] -O
7z x nt_wntr23_filt.cf.7z.001
```

Then you must decompress them with the command:

```
7z x nt_wntr23_filt.cf.7z.001
```

This index was constructed by Jose Manuel Martí, Car Reen Kok, James B. Thissen, Nisha J. Mulakken, Aram Avila-Herrera, Crystal J. Jaing, Jonathan E. Allen, and Nicholas A. Be at LLNL.

[cent_bavm_comp]: https://genome-idx.s3.amazonaws.com/centrifuge/p_compressed%2Bh%2Bv.tar.gz
[cent_bavm_comp_s3]: s3://genome-idx/centrifuge/p_compressed%2Bh%2Bv.tar.gz

[cent_bavm]: https://genome-idx.s3.amazonaws.com/centrifuge/p%2Bh%2Bv.tar.gz
[cent_bavm_s3]: s3://genome-idx/centrifuge/p%2Bh%2Bv.tar.gz

[cent_ba_comp]: https://genome-idx.s3.amazonaws.com/centrifuge/p_compressed_2018_4_15.tar.gz
[cent_ba_comp_s3]: s3://genome-idx/centrifuge/p_compressed_2018_4_15.tar.gz

[cent_nt]: https://genome-idx.s3.amazonaws.com/centrifuge/nt_2018_3_3.tar.gz
[cent_nt_s3]: s3://genome-idx/centrifuge/nt_2018_3_3.tar.gz
