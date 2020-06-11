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
Human   | hg19 | [UCSC][bt2_hg19_source] | [full zip][bt2_hg19_full], [.1.bt2][bt2_hg19_1], [.2.bt2][bt2_hg19_2], [.3.bt2][bt2_hg19_3], [.4.bt2][bt2_hg19_4], [.rev.1.bt2][bt2_hg19_r1], [.rev.2.bt2][bt2_hg19_r2]
Human   | hg18 | [UCSC][bt2_hg18_source] | [full zip][bt2_hg18_full], [.1.bt2][bt2_hg18_1], [.2.bt2][bt2_hg18_2], [.3.bt2][bt2_hg18_3], [.4.bt2][bt2_hg18_4], [.rev.1.bt2][bt2_hg18_r1], [.rev.2.bt2][bt2_hg18_r2]
Mouse   | mm10 | [UCSC][bt2_mm10_source] | [full zip][bt2_mm10_full], [.1.bt2][bt2_mm10_1], [.2.bt2][bt2_mm10_2], [.3.bt2][bt2_mm10_3], [.4.bt2][bt2_mm10_4], [.rev.1.bt2][bt2_mm10_r1], [.rev.2.bt2][bt2_mm10_r2]
Mouse   | mm9 | [UCSC][bt2_mm9_source] | [full zip][bt2_mm9_full], [.1.bt2][bt2_mm9_1], [.2.bt2][bt2_mm9_2], [.3.bt2][bt2_mm9_3], [.4.bt2][bt2_mm9_4], [.rev.1.bt2][bt2_mm9_r1], [.rev.2.bt2][bt2_mm9_r2]
Rat   | rn4 | [UCSC][bt2_rn4_source] | [full zip][bt2_rn4_full], [.1.bt2][bt2_rn4_1], [.2.bt2][bt2_rn4_2], [.3.bt2][bt2_rn4_3], [.4.bt2][bt2_rn4_4], [.rev.1.bt2][bt2_rn4_r1], [.rev.2.bt2][bt2_rn4_r2]

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

[bt2_hg19_source]: https://aws.amazon.com
[bt2_hg19_full]: https://aws.amazon.com
[bt2_hg19_1]: https://aws.amazon.com
[bt2_hg19_2]: https://aws.amazon.com
[bt2_hg19_3]: https://aws.amazon.com
[bt2_hg19_4]: https://aws.amazon.com
[bt2_hg19_r1]: https://aws.amazon.com
[bt2_hg19_r2]: https://aws.amazon.com

[bt2_hg18_source]: https://aws.amazon.com
[bt2_hg18_full]: https://aws.amazon.com
[bt2_hg18_1]: https://aws.amazon.com
[bt2_hg18_2]: https://aws.amazon.com
[bt2_hg18_3]: https://aws.amazon.com
[bt2_hg18_4]: https://aws.amazon.com
[bt2_hg18_r1]: https://aws.amazon.com
[bt2_hg18_r2]: https://aws.amazon.com

[bt2_mm10_source]: https://aws.amazon.com
[bt2_mm10_full]: https://aws.amazon.com
[bt2_mm10_1]: https://aws.amazon.com
[bt2_mm10_2]: https://aws.amazon.com
[bt2_mm10_3]: https://aws.amazon.com
[bt2_mm10_4]: https://aws.amazon.com
[bt2_mm10_r1]: https://aws.amazon.com
[bt2_mm10_r2]: https://aws.amazon.com

[bt2_mm9_source]: https://aws.amazon.com
[bt2_mm9_full]: https://aws.amazon.com
[bt2_mm9_1]: https://aws.amazon.com
[bt2_mm9_2]: https://aws.amazon.com
[bt2_mm9_3]: https://aws.amazon.com
[bt2_mm9_4]: https://aws.amazon.com
[bt2_mm9_r1]: https://aws.amazon.com
[bt2_mm9_r2]: https://aws.amazon.com

[bt2_rn4_source]: https://aws.amazon.com
[bt2_rn4_full]: https://aws.amazon.com
[bt2_rn4_1]: https://aws.amazon.com
[bt2_rn4_2]: https://aws.amazon.com
[bt2_rn4_3]: https://aws.amazon.com
[bt2_rn4_4]: https://aws.amazon.com
[bt2_rn4_r1]: https://aws.amazon.com
[bt2_rn4_r2]: https://aws.amazon.com

# HISAT2 indexes

There are different types of indexes depending on whether transcripts and/or single-nucleotide variants are included in the graph index:

* "genome": HISAT2 index for linear reference
* "snp": HISAT2 index for graph reference including SNPs
* "tran": HISAT2 index for reference plus annotated transcripts
* "snp+tran": HISAT2 index for reference including SNPs, plus annotated transcripts

Indexes with `rep` in the name require HISAT2 v2.2.0 or above.

<div class="datatable-begin"></div>

Species    | Build      | FASTA source | Files
---------- | ---------  | ------------ | -----------
Human      | GRCh38     | [Ensembl][ht2_grch38_source]    | [genome][ht2_grch38_genome], [snp][ht2_grch38_snp], [tran][ht2_grch38_tran], [snp+tran][ht2_grch38_snptran], [rep][ht2_grch38_rep], [snp+rep][ht2_grch38_snprep]
Human      | hg38       | [UCSC][ht2_hg38_source]         | [genome][ht2_hg38_genome], [tran][ht2_hg38_tran]
Human      | GRCh37     | [NCBI][ht2_grch37_source]       | [genome][ht2_grch37_genome], [snp][ht2_grch37_snp], [tran][ht2_grch37_tran], [snp+tran][ht2_grch37_snptran]
Human      | hg19       | [UCSC][ht2_hg19_source]         | [genome][ht2_hg19_genome]
Mouse      | GRCm38     | [NCBI][ht2_grcm38_source]       | [genome][ht2_grcm38_genome], [snp][ht2_grcm38_snp], [tran][ht2_grcm38_tran], [snp+tran][ht2_grcm38_snptran]
Mouse      | mm10       | [UCSC][ht2_mm10_source]         | [genome][ht2_mm10_genome]
Rat        | rn6        | [UCSC][ht2_rn6_source]          | [genome][ht2_rn6_genome]
Drosophila | BDGP6      | [Ensembl][ht2_bdgp6_source]     | [genome][ht2_bdgp6_genome], [tran][ht2_bdgp6_tran]
Drosophila | dm6        | [UCSC][ht2_dm6_source]          | [genome][ht2_dm6_genome]
C. elegans | WBcel235   | [Ensembl][ht2_wbcel235_source]  | [genome][ht2_wbcel235_genome], [tran][ht2_wbcel235_tran]

<div class="datatable-end"></div>

[ht2_grch38_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_grch38.sh
[ht2_grch38_genome]: https://cloud.biohpc.swmed.edu/index.php/s/grch38/download
[ht2_grch38_snp]: https://cloud.biohpc.swmed.edu/index.php/s/grch38_snp/download
[ht2_grch38_tran]: https://cloud.biohpc.swmed.edu/index.php/s/grch38_tran/download
[ht2_grch38_snptran]: https://cloud.biohpc.swmed.edu/index.php/s/grch38_snp_tran/download
[ht2_grch38_rep]: https://cloud.biohpc.swmed.edu/index.php/s/grch38_rep/download
[ht2_grch38_snprep]: https://cloud.biohpc.swmed.edu/index.php/s/grch38_snp_rep/download

[ht2_hg38_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_hg38.sh
[ht2_hg38_genome]: https://cloud.biohpc.swmed.edu/index.php/s/hg38/download
[ht2_hg38_tran]: https://cloud.biohpc.swmed.edu/index.php/s/hg38_tran/download

[ht2_grch37_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_grch37.sh
[ht2_grch37_genome]: https://cloud.biohpc.swmed.edu/index.php/s/grch37/download
[ht2_grch37_snp]: https://cloud.biohpc.swmed.edu/index.php/s/grch37_snp/download
[ht2_grch37_tran]: https://cloud.biohpc.swmed.edu/index.php/s/grch37_tran/download
[ht2_grch37_snptran]: https://cloud.biohpc.swmed.edu/index.php/s/grch37_snp_tran/download

[ht2_hg19_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_hg19.sh
[ht2_hg19_genome]: https://cloud.biohpc.swmed.edu/index.php/s/hg19/download

[ht2_grcm38_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_grcm38.sh
[ht2_grcm38_genome]: https://cloud.biohpc.swmed.edu/index.php/s/grcm38/download
[ht2_grcm38_snp]: https://cloud.biohpc.swmed.edu/index.php/s/grcm38_snp/download
[ht2_grcm38_tran]: https://cloud.biohpc.swmed.edu/index.php/s/grcm38_tran/download
[ht2_grcm38_snptran]: https://cloud.biohpc.swmed.edu/index.php/s/grcm38_snp_tran/download

[ht2_mm10_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_mm10.sh
[ht2_mm10_genome]: https://cloud.biohpc.swmed.edu/index.php/s/mm10/download

[ht2_rn6_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_rn6.sh
[ht2_rn6_genome]: https://cloud.biohpc.swmed.edu/index.php/s/rn6/download

[ht2_bdgp6_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_bdgp6.sh
[//]: # ([ht2_bdgp6_genome]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/data/bdgp6.tar.gz)
[//]: # ([ht2_bdgp6_tran]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/data/bdgp6_tran.tar.gz)
[ht2_bdgp6_genome]: https://aws.amazon.com
[ht2_bdgp6_tran]: https://aws.amazon.com

[ht2_dm6_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_dm6.sh
[//]: # ([ht2_dm6_genome]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/data/dm6.tar.gz)
[ht2_dm6_genome]: https://aws.amazon.com

[ht2_wbcel235_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_wbcel235.sh
[//]: # ([ht2_wbcel235_genome]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/data/wbcel235.tar.gz)
[//]: # ([ht2_wbcel235_tran]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat2/data/wbcel235_tran.tar.gz)
[ht2_wbcel235_genome]: https://aws.amazon.com
[ht2_wbcel235_tran]: https://aws.amazon.com

# HISAT-genotype allele files

Species | Build | FASTA source | Files
------- | ---------  | ------------ | -----------
Human | GRCh38 | NCBI? | [genotypes][htg_genotypes]

[htg_genotypes]: ftp://ftp.ccb.jhu.edu/pub/infphilo/hisat-genotype/data/genotype_genome_20180128.tar.gz

# Kraken 2 / Bracken Refseq indexes

[Kraken 2](https://github.com/DerrickWood/kraken2/wiki) is a fast and memory efficient tool for taxonomic assignment of metagenomics sequencing reads.  [Bracken](https://ccb.jhu.edu/software/bracken/) is a related tool that additionally estimates relative abundances of species or genera.

See the Kraken 2 manual for more information about the individual libraries and their relationship to public repositories.

All packages contain a Kraken 2 database along with Bracken databases built for 100mers, 150mers, and 200mers.

<div class="datatable-begin"></div>

Collection    |     Contains                            | Date             | Size  | Files
------------- | --------------------------------------- | ---------------- | ----- | -----------
Minikraken v1 | Refseq: bacteria, archaea, viral        | March, 2020      |  8 GB | [.tar.gz][k2_mini_v1]
Minikraken v2 | Refseq: bacteria, archaea, viral, human | March, 2020      |  8 GB | [.tar.gz][k2_mini_v2]

<div class="datatable-end"></div>

[k2_mini_v1]: https://aws.amazon.com
[k2_mini_v2]: https://aws.amazon.com
[//]: # ([k2_mini_v1]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/old/minikraken2_v1_8GB_201904.tgz)
[//]: # ([k2_mini_v2]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/old/minikraken2_v2_8GB_201904.tgz)

# Kraken 2 / Bracken 16s RNA indexes

All packages contain a Kraken 2 database along with Bracken databases built for 100mers, 150mers, and 200mers.

<div class="datatable-begin"></div>

Collection              | Date             | Size     | Files
----------------------- | ---------------- | -------- | -----------
Greengenes 13.5         |  March, 2020     | 73.2 MB  | [.tar.gz][k2_16s_greengenes_135]
RDP 11.5                |  March, 2020     | 168 MB   | [.tar.gz][k2_16s_rdp_115]
Silva 132               |  March, 2020     | 117 MB   | [.tar.gz][k2_16s_silva_132]
Silva 138               |  March, 2020     | 112 MB   | [.tar.gz][k2_16s_silva_138]

<div class="datatable-end"></div>

[k2_16s_greengenes_135]: https://aws.amazon.com
[k2_16s_rdp_115]: https://aws.amazon.com
[k2_16s_silva_132]: https://aws.amazon.com
[k2_16s_silva_138]: https://aws.amazon.com

[//]: # ([k2_16s_greengenes_135]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Greengenes13.5_20200326.tgz)
[//]: # ([k2_16s_rdp_115]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_RDP11.5_20200326.tgz)
[//]: # ([k2_16s_silva_132]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Silva132_20200326.tgz)
[//]: # ([k2_16s_silva_138]: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/16S_Silva138_20200326.tgz)

# Centrifuge indexes

Centrifuge is a very rapid and memory-efficient system for the classification of DNA sequences from microbial samples.

<div class="datatable-begin"></div>

Collection                                           | Date            | Size    | Files
---------------------------------------–------------ | --------------- | ------- | --------------------
Refseq: bacteria, archaea, viral, human (compressed) |  December, 2016 | 5.4 GB  | [.tar.gz][cent_bavm_comp]
Refseq: bacteria, archaea, viral, human              |  December, 2016 | 7.9 GB  | [.tar.gz][cent_bavm]
Refseq: bacteria, archaea (compressed)               |  April, 2018    | 64 GB   | [.tar.gz][cent_ba_comp]
NCBI: nucleotide non-redundant sequences             |  March, 2018    | 6.3 GB  | [.tar.gz][cent_nt]

<div class="datatable-end"></div>

[cent_bavm_comp]: https://aws.amazon.com
[cent_bavm]: https://aws.amazon.com
[cent_ba_comp]: https://aws.amazon.com
[cent_nt]: https://aws.amazon.com

[//]: # ([cent_bavm_comp]: ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/p_compressed+h+v.tar.gz)
[//]: # ([cent_bavm]: ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/p+h+v.tar.gz)
[//]: # ([cent_ba_comp]: ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/p_compressed_2018_4_15.tar.gz)
[//]: # ([cent_nt]: ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/nt_2018_3_3.tar.gz)
