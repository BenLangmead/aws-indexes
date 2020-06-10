Public hosting of these index files is possible thanks to the Amazon Web Services [Public Dataset Program](https://aws.amazon.com/opendata/public-datasets/).

# Bowtie 2 indexes

[Bowtie](http://bowtie-bio.sourceforge.net) and [Bowtie 2](http://bowtie-bio.sourceforge.net/bowtie2) are read aligners for sequencing reads.  Bowtie specializes in short reads, generally about 50bp or shorter.  Bowtie 2 specializes in longer reads, up to around hundreds of base pairs.

In the past, Bowtie 1 & 2 had incompatible genome indexes.  This changed in July 2019 when Bowtie v1.2.3 gained the ability to use Bowtie 2 formatted genome indexes (ending in `.bt2`).  We list only Bowtie 2-format `.bt2` index files here.

See the manuals for Bowtie & Bowtie 2 for further details.

Note: all links are placeholders for now.  They will be replaced when the public repo is available.

<div class="datatable-begin"></div>

Species | Build      | FASTA source | Files
------- | ---------  | ------------ | -----------
Human   | hg38       | [UCSC][bt2_hg38_source] | [full zip][bt2_hg38_full], [.1.bt2][bt2_hg38_1], [.2.bt2][bt2_hg38_2], [.3.bt2][bt2_hg38_3], [.4.bt2][bt2_hg38_4], [.rev.1.bt2][bt2_hg38_r1], [.rev.2.bt2][bt2_hg38_r2]
Human   | GRCh38     | [NCBI][bt2_GRCh38_source]     | [full zip][bt2_GRCh38_full], [.1.bt2][bt2_GRCh38_1], [.2.bt2][bt2_GRCh38_2], [.3.bt2][bt2_GRCh38_3], [.4.bt2][bt2_GRCh38_4], [.rev.1.bt2][bt2_GRCh38_r1], [.rev.2.bt2][bt2_GRCh38_r2]
Human   | GRCh38 + major SNVs* | [NCBI][bt2_grch38_1kgmaj_source] | [full zip][bt2_grch38_1kgmaj_full], [.1.bt2][bt2_grch38_1kgmaj_1], [.2.bt2][bt2_grch38_1kgmaj_2], [.3.bt2][bt2_grch38_1kgmaj_3], [.4.bt2][bt2_grch38_1kgmaj_4], [.rev.1.bt2][bt2_grch38_1kgmaj_r1], [.rev.2.bt2][bt2_grch38_1kgmaj_r2]

<div class="datatable-end"></div>

* Major SNVs determined from [1000 Genomes Project](https://www.internationalgenome.org) variant calls.  [Details here](https://github.com/BenLangmead/bowtie-majref).

[bt2_hg38_source]: https://aws.amazon.com
[bt2_hg38_full]: https://aws.amazon.com
[bt2_hg38_1]: https://aws.amazon.com
[bt2_hg38_2]: https://aws.amazon.com
[bt2_hg38_3]: https://aws.amazon.com
[bt2_hg38_4]: https://aws.amazon.com
[bt2_hg38_r1]: https://aws.amazon.com
[bt2_hg38_r2]: https://aws.amazon.com

[bt2_GRCh38_source]: https://aws.amazon.com
[bt2_GRCh38_full]: https://aws.amazon.com
[bt2_GRCh38_1]: https://aws.amazon.com
[bt2_GRCh38_2]: https://aws.amazon.com
[bt2_GRCh38_3]: https://aws.amazon.com
[bt2_GRCh38_4]: https://aws.amazon.com
[bt2_GRCh38_r1]: https://aws.amazon.com
[bt2_GRCh38_r2]: https://aws.amazon.com

[bt2_grch38_1kgmaj_source]: https://aws.amazon.com
[bt2_grch38_1kgmaj_full]: https://aws.amazon.com
[bt2_grch38_1kgmaj_1]: https://aws.amazon.com
[bt2_grch38_1kgmaj_2]: https://aws.amazon.com
[bt2_grch38_1kgmaj_3]: https://aws.amazon.com
[bt2_grch38_1kgmaj_4]: https://aws.amazon.com
[bt2_grch38_1kgmaj_r1]: https://aws.amazon.com
[bt2_grch38_1kgmaj_r2]: https://aws.amazon.com

# HISAT2 indexes

<div class="datatable-begin"></div>

Species | Build      | FASTA source | Files
------- | ---------  | ------------ | -----------
Human   | hg38       | [UCSC]()     | [full zip](), [.1.bt2](), [.2.bt2](), [.3.bt2](), [.4.bt2](), [.rev.1.bt2](), [.rev.2.bt2]()
Human   | GRCh38     | [NCBI]()     | [full zip](), [`.1.bt2`](), [`.2.bt2`](), [`.3.bt2`](), [`.4.bt2`](), [`.rev.1.bt2`](), [`.rev.2.bt2`]()

<div class="datatable-end"></div>

# HISAT-genotype allele files

# Kraken 2 & Bracken indexes

[Kraken 2](https://github.com/DerrickWood/kraken2/wiki) is a fast and memory efficient tool for taxonomic assignment of metagenomics sequencing reads.  [Bracken](https://ccb.jhu.edu/software/bracken/) is a related tool that additionally estimates relative abundances of species or genera.

See the Kraken 2 manual for more information about the individual libraries and their relationship to public repositories.

<div class="datatable-begin"></div>

Collection | Libraries  | Files
---------- | ---------  | -----------
Minikraken | hg38       | [hash.k2d](), [opts.k2d](), [taxo.k2d](), [Bracken]
Human      | GRCh38     | [hash.k2d](), [opts.k2d](), [taxo.k2d](), [Bracken]

<div class="datatable-end"></div>
