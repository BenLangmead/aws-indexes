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
