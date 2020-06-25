# HISAT2 indexes

There are different types of indexes depending on whether transcripts and/or single-nucleotide variants are included in the graph index:

* "genome": HISAT2 index for linear reference
* "snp": HISAT2 index for graph reference including SNPs
* "tran": HISAT2 index for reference plus annotated transcripts
* "snp+tran": HISAT2 index for reference including SNPs, plus annotated transcripts
* "rep": HISAT2 repeat index for reference
* "snp+rep": HISAT2 repeat index for reference including SNPs

Indexes with `rep` in the name require HISAT2 v2.2.0 or above.

<div class="datatable-begin"></div>

Species / Build         | FASTA source                    | HTTPS URL                                                                                                                                                         | S3 URL
----------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------
Human      / GRCh38     | [Ensembl][ht2_grch38_source]    | [genome][ht2_grch38_genome], [snp][ht2_grch38_snp], [tran][ht2_grch38_tran], [snp+tran][ht2_grch38_snptran], [rep][ht2_grch38_rep], [snp+rep][ht2_grch38_snprep]  | [genome][ht2_grch38_genome_s3], [snp][ht2_grch38_snp_s3], [tran][ht2_grch38_tran_s3], [snp+tran][ht2_grch38_snptran_s3], [rep][ht2_grch38_rep_s3], [snp+rep][ht2_grch38_snprep_s3]
Human      / hg38       | [UCSC][ht2_hg38_source]         | [genome][ht2_hg38_genome], [tran][ht2_hg38_tran]                                                                                                                  | [genome][ht2_hg38_genome_s3], [tran][ht2_hg38_tran_s3]
Human      / GRCh37     | [NCBI][ht2_grch37_source]       | [genome][ht2_grch37_genome], [snp][ht2_grch37_snp], [tran][ht2_grch37_tran], [snp+tran][ht2_grch37_snptran]                                                       | [genome][ht2_grch37_genome_s3], [snp][ht2_grch37_snp_s3], [tran][ht2_grch37_tran_s3], [snp+tran][ht2_grch37_snptran_s3]
Human      / hg19       | [UCSC][ht2_hg19_source]         | [genome][ht2_hg19_genome]                                                                                                                                         | [genome][ht2_hg19_genome_s3]
Mouse      / GRCm38     | [NCBI][ht2_grcm38_source]       | [genome][ht2_grcm38_genome], [snp][ht2_grcm38_snp], [tran][ht2_grcm38_tran], [snp+tran][ht2_grcm38_snptran]                                                       | [genome][ht2_grcm38_genome_s3], [snp][ht2_grcm38_snp_s3], [tran][ht2_grcm38_tran_s3], [snp+tran][ht2_grcm38_snptran_s3]
Mouse      / mm10       | [UCSC][ht2_mm10_source]         | [genome][ht2_mm10_genome]                                                                                                                                         | [genome][ht2_mm10_genome_s3] 
Rat        / rn6        | [UCSC][ht2_rn6_source]          | [genome][ht2_rn6_genome]                                                                                                                                          | [genome][ht2_rn6_genome_s3]
Drosophila / BDGP6      | [Ensembl][ht2_bdgp6_source]     | [genome][ht2_bdgp6_genome], [tran][ht2_bdgp6_tran]                                                                                                                | [genome][ht2_bdgp6_genome_s3], [tran][ht2_bdgp6_tran_s3]
Drosophila / dm6        | [UCSC][ht2_dm6_source]          | [genome][ht2_dm6_genome]                                                                                                                                          | [genome][ht2_dm6_genome_s3] 
C. elegans / WBcel235   | [Ensembl][ht2_wbcel235_source]  | [genome][ht2_wbcel235_genome], [tran][ht2_wbcel235_tran]                                                                                                          | [genome][ht2_wbcel235_genome_s3], [tran][ht2_wbcel235_tran_s3]

<div class="datatable-end"></div>

[ht2_grch38_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_grch38.sh
[ht2_grch38_genome]: https://genome-idx.s3.amazonaws.com/hisat/grch38_genome.tar.gz
[ht2_grch38_genome_s3]: s3://genome-idx/hisat/grch38_genome.tar.gz
[ht2_grch38_snp]: https://genome-idx.s3.amazonaws.com/hisat/grch38_snp.tar.gz
[ht2_grch38_snp_s3]: s3://genome-idx/hisat/grch38_snp.tar.gz
[ht2_grch38_tran]: https://genome-idx.s3.amazonaws.com/hisat/grch38_tran.tar.gz
[ht2_grch38_tran_s3]: s3://genome-idx/hisat/grch38_tran.tar.gz
[ht2_grch38_snptran]: https://genome-idx.s3.amazonaws.com/hisat/grch38_snp_tran.tar.gz
[ht2_grch38_snptran_s3]: s3://genome-idx/hisat/grch38_snp_tran.tar.gz
[ht2_grch38_rep]: https://genome-idx.s3.amazonaws.com/hisat/grch38_rep.tar.gz
[ht2_grch38_rep_s3]: s3://genome-idx/hisat/grch38_rep.tar.gz
[ht2_grch38_snprep]: https://genome-idx.s3.amazonaws.com/hisat/grch38_snprep.tar.gz
[ht2_grch38_snprep_s3]: s3://genome-idx/hisat/grch38_snprep.tar.gz

[ht2_hg38_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_hg38.sh
[ht2_hg38_genome]: https://genome-idx.s3.amazonaws.com/hisat/hg38.tar.gz
[ht2_hg38_genome_s3]: s3://genome-idx/hisat/hg38.tar.gz
[ht2_hg38_tran]: https://genome-idx.s3.amazonaws.com/hisat/hg38_tran.tar.gz
[ht2_hg38_tran_s3]: s3://genome-idx/hisat/hg38_tran.tar.gz

[ht2_grch37_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_grch37.sh
[ht2_grch37_genome]: https://genome-idx.s3.amazonaws.com/hisat/grch37_genome.tar.gz
[ht2_grch37_genome_s3]: s3://genome-idx/hisat/grch37_genome.tar.gz
[ht2_grch37_snp]: https://genome-idx.s3.amazonaws.com/hisat/grch37_snp.tar.gz
[ht2_grch37_snp_s3]: s3://genome-idx/hisat/grch37_snp.tar.gz
[ht2_grch37_tran]: https://genome-idx.s3.amazonaws.com/hisat/grch37_tran.tar.gz
[ht2_grch37_tran_s3]: s3://genome-idx/hisat/grch37_tran.tar.gz
[ht2_grch37_snptran]: https://genome-idx.s3.amazonaws.com/hisat/grch37_snptran.tar.gz
[ht2_grch37_snptran_s3]: s3://genome-idx/hisat/grch37_snptran.tar.gz

[ht2_hg19_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_hg19.sh
[ht2_hg19_genome]: https://genome-idx.s3.amazonaws.com/hisat/hg19_genome.tar.gz
[ht2_hg19_genome_s3]: s3://genome-idx/hisat/hg19_genome.tar.gz

[ht2_grcm38_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_grcm38.sh
[ht2_grcm38_genome]: https://genome-idx.s3.amazonaws.com/hisat/grcm38_genome.tar.gz
[ht2_grcm38_genome_s3]: s3://genome-idx/hisat/grcm38_genome.tar.gz
[ht2_grcm38_snp]: https://genome-idx.s3.amazonaws.com/hisat/grcm38_snp.tar.gz
[ht2_grcm38_snp_s3]: s3://genome-idx/hisat/grcm38_snp.tar.gz
[ht2_grcm38_tran]: https://genome-idx.s3.amazonaws.com/hisat/grcm38_tran.tar.gz
[ht2_grcm38_tran_s3]: s3://genome-idx/hisat/grcm38_tran.tar.gz
[ht2_grcm38_snptran]: https://genome-idx.s3.amazonaws.com/hisat/grcm38_snptran.tar.gz
[ht2_grcm38_snptran_s3]: s3://genome-idx/hisat/grcm38_snptran.tar.gz

[ht2_mm10_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_mm10.sh
[ht2_mm10_genome]: https://genome-idx.s3.amazonaws.com/hisat/mm10_genome.tar.gz
[ht2_mm10_genome_s3]: s3://genome-idx/hisat/mm10_genome.tar.gz

[ht2_rn6_source]: https://github.com/DaehwanKimLab/hisat2/blob/master/scripts/make_rn6.sh
[ht2_rn6_genome]: https://genome-idx.s3.amazonaws.com/hisat/rn6_genome.tar.gz
[ht2_rn6_genome_s3]: s3://genome-idx/hisat/rn6_genome.tar.gz

[ht2_bdgp6_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_bdgp6.sh
[ht2_bdgp6_genome]: https://genome-idx.s3.amazonaws.com/hisat/bdgp6.tar.gz
[ht2_bdgp6_genome_s3]: s3://genome-idx/hisat/bdgp6.tar.gz
[ht2_bdgp6_tran]: https://genome-idx.s3.amazonaws.com/hisat/bdgp6_tran.tar.gz
[ht2_bdgp6_tran_s3]: s3://genome-idx/hisat/bdgp6_tran.tar.gz

[ht2_dm6_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_dm6.sh
[ht2_dm6_genome]: https://genome-idx.s3.amazonaws.com/hisat/dm6.tar.gz
[ht2_dm6_genome_s3]: s3://genome-idx/hisat/dm6.tar.gz

[ht2_wbcel235_source]: https://github.com/infphilo/hisat2/blob/master/scripts/make_wbcel235.sh
[ht2_wbcel235_genome]: https://genome-idx.s3.amazonaws.com/hisat/wbcel235.tar.gz
[ht2_wbcel235_genome_s3]: s3://genome-idx/hisat/wbcel235.tar.gz
[ht2_wbcel235_tran]: https://genome-idx.s3.amazonaws.com/hisat/wbcel235_tran.tar.gz
[ht2_wbcel235_tran_s3]: s3://genome-idx/hisat/wbcel235_tran.tar.gz

# HISAT-genotype allele files

Species / Build | HTTPs URLs | S3 URLs
------- | ---------  | ------------
Human / GRCh38 | [genotypes][htg_genotypes] | [genotypes][htg_genotypes_s3]

[htg_genotypes]: https://genome-idx.s3.amazonaws.com/hisat/genotype_genome_20180128.tar.gz
[htg_genotypes_s3]: s3://genome-idx/hisat/genotype_genome_20180128.tar.gz
