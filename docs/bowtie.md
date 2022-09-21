# Bowtie 2 indexes

[Bowtie](http://bowtie-bio.sourceforge.net) and [Bowtie 2](http://bowtie-bio.sourceforge.net/bowtie2) are read aligners for sequencing reads.  Bowtie specializes in short reads, generally about 50bp or shorter.  Bowtie 2 specializes in longer reads, up to around hundreds of base pairs.  HTTPS URLs allow you to download the files from your web browser or using command-line tools like `wget` or `curl`.  The S3 URLs can be used with AWS tools, including the [AWS console](https://aws.amazon.com/console/) and [AWS command-line interface](https://aws.amazon.com/cli/). 

In the past, Bowtie 1 & 2 had incompatible genome indexes.  This changed in July 2019 when Bowtie v1.2.3 gained the ability to use Bowtie 2 formatted genome indexes (ending in `.bt2`).  We list only Bowtie 2-format `.bt2` index files here.

You can download all the files for a given assembly as a single `zip` file, or as 6 separate `.bt2` files.  For example, if you only need the forward version of the genome index (e.g. for exact matching only), you can download the files individually and omit the `.rev.1.bt2` and `.rev.2.bt2` files.  Downloading already-decompressed index files might also be quicker for applications running in the AWS cloud.

<div class="datatable-begin"></div>

Species/Build                             | Source                                            | HTTPS URLs  | S3 URLs                                                                                                                                                                                                                               
----------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ 
Human / GRCh38 no-alt analysis set<sup>1</sup> | [NCBI][bt2_grch38_noalt_source] | [full zip][bt2_grch38_noalt_full], [.1.bt2][bt2_grch38_noalt_1], [.2.bt2][bt2_grch38_noalt_2], [.3.bt2][bt2_grch38_noalt_3], [.4.bt2][bt2_grch38_noalt_4], [.rev.1.bt2][bt2_grch38_noalt_r1], [.rev.2.bt2][bt2_grch38_noalt_r2] | [full zip][bt2_grch38_noalt_full_s3], [.1.bt2][bt2_grch38_noalt_1_s3], [.2.bt2][bt2_grch38_noalt_2_s3], [.3.bt2][bt2_grch38_noalt_3_s3], [.4.bt2][bt2_grch38_noalt_4_s3], [.rev.1.bt2][bt2_grch38_noalt_r1_s3], [.rev.2.bt2][bt2_grch38_noalt_r2_s3]
Human / GRCh38 no-alt +decoy set<sup>1</sup> | [NCBI][bt2_grch38_noalt_decoy_source] | [full zip][bt2_grch38_noalt_decoy_full], [.1.bt2][bt2_grch38_noalt_decoy_1], [.2.bt2][bt2_grch38_noalt_decoy_2], [.3.bt2][bt2_grch38_noalt_decoy_3], [.4.bt2][bt2_grch38_noalt_decoy_4], [.rev.1.bt2][bt2_grch38_noalt_decoy_r1], [.rev.2.bt2][bt2_grch38_noalt_decoy_r2] | [full zip][bt2_grch38_noalt_decoy_full_s3], [.1.bt2][bt2_grch38_noalt_decoy_1_s3], [.2.bt2][bt2_grch38_noalt_decoy_2_s3], [.3.bt2][bt2_grch38_noalt_decoy_3_s3], [.4.bt2][bt2_grch38_noalt_decoy_4_s3], [.rev.1.bt2][bt2_grch38_noalt_decoy_r1_s3], [.rev.2.bt2][bt2_grch38_noalt_decoy_r2_s3]
Human / GRCh38 + major SNVs | [NCBI+1KG<sup>2</sup>][bt2_grch38_1kgmaj_source] | [full zip][bt2_grch38_1kgmaj_full], [.1.bt2][bt2_grch38_1kgmaj_1], [.2.bt2][bt2_grch38_1kgmaj_2], [.3.bt2][bt2_grch38_1kgmaj_3], [.4.bt2][bt2_grch38_1kgmaj_4], [.rev.1.bt2][bt2_grch38_1kgmaj_r1], [.rev.2.bt2][bt2_grch38_1kgmaj_r2] | [full zip][bt2_grch38_1kgmaj_full_s3], [.1.bt2][bt2_grch38_1kgmaj_1_s3], [.2.bt2][bt2_grch38_1kgmaj_2_s3], [.3.bt2][bt2_grch38_1kgmaj_3_s3], [.4.bt2][bt2_grch38_1kgmaj_4_s3], [.rev.1.bt2][bt2_grch38_1kgmaj_r1_s3], [.rev.2.bt2][bt2_grch38_1kgmaj_r2_s3]
Human / CHM13plusY | [T2T<sup>3</sup>][bt2_t2tplusy_source] | [full zip][bt2_t2tplusy_full], [.1.bt2][bt2_t2tplusy_1], [.2.bt2][bt2_t2tplusy_2], [.3.bt2][bt2_t2tplusy_3], [.4.bt2][bt2_t2tplusy_4], [.rev.1.bt2][bt2_t2tplusy_r1], [.rev.2.bt2][bt2_t2tplusy_r2] | [full zip][bt2_t2tplusy_full_s3], [.1.bt2][bt2_t2tplusy_1_s3], [.2.bt2][bt2_t2tplusy_2_s3], [.3.bt2][bt2_t2tplusy_3_s3], [.4.bt2][bt2_t2tplusy_4_s3], [.rev.1.bt2][bt2_t2tplusy_r1_s3], [.rev.2.bt2][bt2_t2tplusy_r2_s3]
Human / GRCh37 | [NCBI][bt2_grch37_source] | [full zip][bt2_grch37_full], [.1.bt2][bt2_grch37_1], [.2.bt2][bt2_grch37_2], [.3.bt2][bt2_grch37_3], [.4.bt2][bt2_grch37_4], [.rev.1.bt2][bt2_grch37_r1], [.rev.2.bt2][bt2_grch37_r2] | [full zip][bt2_grch37_full_s3], [.1.bt2][bt2_grch37_1_s3], [.2.bt2][bt2_grch37_2_s3], [.3.bt2][bt2_grch37_3_s3], [.4.bt2][bt2_grch37_4_s3], [.rev.1.bt2][bt2_grch37_r1_s3], [.rev.2.bt2][bt2_grch37_r2_s3]
Human / Ash2.0 | [JHU<sup>4</sup>][bt2_ash1_2_source] | [full zip][bt2_ash1_2_full], [.1.bt2][bt2_ash1_2_1], [.2.bt2][bt2_ash1_2_2], [.3.bt2][bt2_ash1_2_3], [.4.bt2][bt2_ash1_2_4], [.rev.1.bt2][bt2_ash1_2_r1], [.rev.2.bt2][bt2_ash1_2_r2] | [full zip][bt2_ash1_2_full_s3], [.1.bt2][bt2_ash1_2_1_s3], [.2.bt2][bt2_ash1_2_2_s3], [.3.bt2][bt2_ash1_2_3_s3], [.4.bt2][bt2_ash1_2_4_s3], [.rev.1.bt2][bt2_ash1_2_r1_s3], [.rev.2.bt2][bt2_ash1_2_r2_s3]
Human / Ash1.7 | [JHU<sup>4</sup>][bt2_ash1_source] | [full zip][bt2_ash1_full], [.1.bt2][bt2_ash1_1], [.2.bt2][bt2_ash1_2], [.3.bt2][bt2_ash1_3], [.4.bt2][bt2_ash1_4], [.rev.1.bt2][bt2_ash1_r1], [.rev.2.bt2][bt2_ash1_r2] | [full zip][bt2_ash1_full_s3], [.1.bt2][bt2_ash1_1_s3], [.2.bt2][bt2_ash1_2_s3], [.3.bt2][bt2_ash1_3_s3], [.4.bt2][bt2_ash1_4_s3], [.rev.1.bt2][bt2_ash1_r1_s3], [.rev.2.bt2][bt2_ash1_r2_s3]
Human / hg19 | [UCSC][bt2_hg19_source] | [full zip][bt2_hg19_full], [.1.bt2][bt2_hg19_1], [.2.bt2][bt2_hg19_2], [.3.bt2][bt2_hg19_3], [.4.bt2][bt2_hg19_4], [.rev.1.bt2][bt2_hg19_r1], [.rev.2.bt2][bt2_hg19_r2] | [full zip][bt2_hg19_full_s3], [.1.bt2][bt2_hg19_1_s3], [.2.bt2][bt2_hg19_2_s3], [.3.bt2][bt2_hg19_3_s3], [.4.bt2][bt2_hg19_4_s3], [.rev.1.bt2][bt2_hg19_r1_s3], [.rev.2.bt2][bt2_hg19_r2_s3]
Human / hg18 | [UCSC][bt2_hg18_source] | [full zip][bt2_hg18_full], [.1.bt2][bt2_hg18_1], [.2.bt2][bt2_hg18_2], [.3.bt2][bt2_hg18_3], [.4.bt2][bt2_hg18_4], [.rev.1.bt2][bt2_hg18_r1], [.rev.2.bt2][bt2_hg18_r2] | [full zip][bt2_hg18_full_s3], [.1.bt2][bt2_hg18_1_s3], [.2.bt2][bt2_hg18_2_s3], [.3.bt2][bt2_hg18_3_s3], [.4.bt2][bt2_hg18_4_s3], [.rev.1.bt2][bt2_hg18_r1_s3], [.rev.2.bt2][bt2_hg18_r2_s3]
Mouse / GRCm38 | [NCBI][bt2_grcm38_source] | [full zip][bt2_grcm38_full], [.1.bt2][bt2_grcm38_1], [.2.bt2][bt2_grcm38_2], [.3.bt2][bt2_grcm38_3], [.4.bt2][bt2_grcm38_4], [.rev.1.bt2][bt2_grcm38_r1], [.rev.2.bt2][bt2_grcm38_r2] | [full zip][bt2_grcm38_full_s3], [.1.bt2][bt2_grcm38_1_s3], [.2.bt2][bt2_grcm38_2_s3], [.3.bt2][bt2_grcm38_3_s3], [.4.bt2][bt2_grcm38_4_s3], [.rev.1.bt2][bt2_grcm38_r1_s3], [.rev.2.bt2][bt2_grcm38_r2_s3]
Mouse / GRCm39 | [NCBI][bt2_grcm39_source] | [full zip][bt2_grcm39_full], [.1.bt2][bt2_grcm39_1], [.2.bt2][bt2_grcm39_2], [.3.bt2][bt2_grcm39_3], [.4.bt2][bt2_grcm39_4], [.rev.1.bt2][bt2_grcm39_r1], [.rev.2.bt2][bt2_grcm39_r2] | [full zip][bt2_grcm39_full_s3], [.1.bt2][bt2_grcm39_1_s3], [.2.bt2][bt2_grcm39_2_s3], [.3.bt2][bt2_grcm39_3_s3], [.4.bt2][bt2_grcm39_4_s3], [.rev.1.bt2][bt2_grcm39_r1_s3], [.rev.2.bt2][bt2_grcm39_r2_s3]
Mouse / mm10 | [UCSC][bt2_mm10_source] | [full zip][bt2_mm10_full], [.1.bt2][bt2_mm10_1], [.2.bt2][bt2_mm10_2], [.3.bt2][bt2_mm10_3], [.4.bt2][bt2_mm10_4], [.rev.1.bt2][bt2_mm10_r1], [.rev.2.bt2][bt2_mm10_r2] | [full zip][bt2_mm10_full_s3], [.1.bt2][bt2_mm10_1_s3], [.2.bt2][bt2_mm10_2_s3], [.3.bt2][bt2_mm10_3_s3], [.4.bt2][bt2_mm10_4_s3], [.rev.1.bt2][bt2_mm10_r1_s3], [.rev.2.bt2][bt2_mm10_r2_s3]
Mouse / mm9 | [UCSC][bt2_mm9_source] | [full zip][bt2_mm9_full], [.1.bt2][bt2_mm9_1], [.2.bt2][bt2_mm9_2], [.3.bt2][bt2_mm9_3], [.4.bt2][bt2_mm9_4], [.rev.1.bt2][bt2_mm9_r1], [.rev.2.bt2][bt2_mm9_r2] | [full zip][bt2_mm9_full_s3], [.1.bt2][bt2_mm9_1_s3], [.2.bt2][bt2_mm9_2_s3], [.3.bt2][bt2_mm9_3_s3], [.4.bt2][bt2_mm9_4_s3], [.rev.1.bt2][bt2_mm9_r1_s3], [.rev.2.bt2][bt2_mm9_r2_s3]
Chimpanzee / Clint_PTRv2 | [NCBI][bt2_clintptr2_source] | [full zip][bt2_clintptr2_full], [.1.bt2][bt2_clintptr2_1], [.2.bt2][bt2_clintptr2_2], [.3.bt2][bt2_clintptr2_3], [.4.bt2][bt2_clintptr2_4], [.rev.1.bt2][bt2_clintptr2_r1], [.rev.2.bt2][bt2_clintptr2_r2] | [full zip][bt2_clintptr2_full_s3], [.1.bt2][bt2_clintptr2_1_s3], [.2.bt2][bt2_clintptr2_2_s3], [.3.bt2][bt2_clintptr2_3_s3], [.4.bt2][bt2_clintptr2_4_s3], [.rev.1.bt2][bt2_clintptr2_r1_s3], [.rev.2.bt2][bt2_clintptr2_r2_s3]
Chimpanzee / CHIMP2.1.4 | [Ensembl][bt2_chimp214_source] | [full zip][bt2_chimp214_full], [.1.bt2][bt2_chimp214_1], [.2.bt2][bt2_chimp214_2], [.3.bt2][bt2_chimp214_3], [.4.bt2][bt2_chimp214_4], [.rev.1.bt2][bt2_chimp214_r1], [.rev.2.bt2][bt2_chimp214_r2] | [full zip][bt2_chimp214_full_s3], [.1.bt2][bt2_chimp214_1_s3], [.2.bt2][bt2_chimp214_2_s3], [.3.bt2][bt2_chimp214_3_s3], [.4.bt2][bt2_chimp214_4_s3], [.rev.1.bt2][bt2_chimp214_r1_s3], [.rev.2.bt2][bt2_chimp214_r2_s3]
Rhesus macaque / MMul_10 | [Ensembl][bt2_mmul10_source] | [full zip][bt2_mmul10_full], [.1.bt2][bt2_mmul10_1], [.2.bt2][bt2_mmul10_2], [.3.bt2][bt2_mmul10_3], [.4.bt2][bt2_mmul10_4], [.rev.1.bt2][bt2_mmul10_r1], [.rev.2.bt2][bt2_mmul10_r2] | [full zip][bt2_mmul10_full_s3], [.1.bt2][bt2_mmul10_1_s3], [.2.bt2][bt2_mmul10_2_s3], [.3.bt2][bt2_mmul10_3_s3], [.4.bt2][bt2_mmul10_4_s3], [.rev.1.bt2][bt2_mmul10_r1_s3], [.rev.2.bt2][bt2_mmul10_r2_s3]
Cow / ARS-UCD1.2 | [NCBI][bt2_arsucd12_source] | [full zip][bt2_arsucd12_full], [.1.bt2][bt2_arsucd12_1], [.2.bt2][bt2_arsucd12_2], [.3.bt2][bt2_arsucd12_3], [.4.bt2][bt2_arsucd12_4], [.rev.1.bt2][bt2_arsucd12_r1], [.rev.2.bt2][bt2_arsucd12_r2] | [full zip][bt2_arsucd12_full_s3], [.1.bt2][bt2_arsucd12_1_s3], [.2.bt2][bt2_arsucd12_2_s3], [.3.bt2][bt2_arsucd12_3_s3], [.4.bt2][bt2_arsucd12_4_s3], [.rev.1.bt2][bt2_arsucd12_r1_s3], [.rev.2.bt2][bt2_arsucd12_r2_s3]
Pig / Sscrofa11.1 | [NCBI][bt2_sscorfa111_source] | [full zip][bt2_sscorfa111_full], [.1.bt2][bt2_sscorfa111_1], [.2.bt2][bt2_sscorfa111_2], [.3.bt2][bt2_sscorfa111_3], [.4.bt2][bt2_sscorfa111_4], [.rev.1.bt2][bt2_sscorfa111_r1], [.rev.2.bt2][bt2_sscorfa111_r2] | [full zip][bt2_sscorfa111_full_s3], [.1.bt2][bt2_sscorfa111_1_s3], [.2.bt2][bt2_sscorfa111_2_s3], [.3.bt2][bt2_sscorfa111_3_s3], [.4.bt2][bt2_sscorfa111_4_s3], [.rev.1.bt2][bt2_sscorfa111_r1_s3], [.rev.2.bt2][bt2_sscorfa111_r2_s3]
Dog / CanFam3.1 | [Ensembl][bt2_canfam31_source] | [full zip][bt2_canfam31_full], [.1.bt2][bt2_canfam31_1], [.2.bt2][bt2_canfam31_2], [.3.bt2][bt2_canfam31_3], [.4.bt2][bt2_canfam31_4], [.rev.1.bt2][bt2_canfam31_r1], [.rev.2.bt2][bt2_canfam31_r2] | [full zip][bt2_canfam31_full_s3], [.1.bt2][bt2_canfam31_1_s3], [.2.bt2][bt2_canfam31_2_s3], [.3.bt2][bt2_canfam31_3_s3], [.4.bt2][bt2_canfam31_4_s3], [.rev.1.bt2][bt2_canfam31_r1_s3], [.rev.2.bt2][bt2_canfam31_r2_s3]
Dog / CanFam4 | [NCBI][bt2_canfam4_source] | [full zip][bt2_canfam4_full], [.1.bt2][bt2_canfam4_1], [.2.bt2][bt2_canfam4_2], [.3.bt2][bt2_canfam4_3], [.4.bt2][bt2_canfam4_4], [.rev.1.bt2][bt2_canfam4_r1], [.rev.2.bt2][bt2_canfam4_r2] | [full zip][bt2_canfam4_full_s3], [.1.bt2][bt2_canfam4_1_s3], [.2.bt2][bt2_canfam4_2_s3], [.3.bt2][bt2_canfam4_3_s3], [.4.bt2][bt2_canfam4_4_s3], [.rev.1.bt2][bt2_canfam4_r1_s3], [.rev.2.bt2][bt2_canfam4_r2_s3]
Rat / rn4 | [UCSC][bt2_rn4_source] | [full zip][bt2_rn4_full], [.1.bt2][bt2_rn4_1], [.2.bt2][bt2_rn4_2], [.3.bt2][bt2_rn4_3], [.4.bt2][bt2_rn4_4], [.rev.1.bt2][bt2_rn4_r1], [.rev.2.bt2][bt2_rn4_r2] | [full zip][bt2_rn4_full_s3], [.1.bt2][bt2_rn4_1_s3], [.2.bt2][bt2_rn4_2_s3], [.3.bt2][bt2_rn4_3_s3], [.4.bt2][bt2_rn4_4_s3], [.rev.1.bt2][bt2_rn4_r1_s3], [.rev.2.bt2][bt2_rn4_r2_s3]
Rat / Rnor6.0 | [NCBI][bt2_rnor60_source] | [full zip][bt2_rnor60_full], [.1.bt2][bt2_rnor60_1], [.2.bt2][bt2_rnor60_2], [.3.bt2][bt2_rnor60_3], [.4.bt2][bt2_rnor60_4], [.rev.1.bt2][bt2_rnor60_r1], [.rev.2.bt2][bt2_rnor60_r2] | [full zip][bt2_rnor60_full_s3], [.1.bt2][bt2_rnor60_1_s3], [.2.bt2][bt2_rnor60_2_s3], [.3.bt2][bt2_rnor60_3_s3], [.4.bt2][bt2_rnor60_4_s3], [.rev.1.bt2][bt2_rnor60_r1_s3], [.rev.2.bt2][bt2_rnor60_r2_s3]
Chicken / GRCg6a | [NCBI][bt2_grcg6a_source] | [full zip][bt2_grcg6a_full], [.1.bt2][bt2_grcg6a_1], [.2.bt2][bt2_grcg6a_2], [.3.bt2][bt2_grcg6a_3], [.4.bt2][bt2_grcg6a_4], [.rev.1.bt2][bt2_grcg6a_r1], [.rev.2.bt2][bt2_grcg6a_r2] | [full zip][bt2_grcg6a_full_s3], [.1.bt2][bt2_grcg6a_1_s3], [.2.bt2][bt2_grcg6a_2_s3], [.3.bt2][bt2_grcg6a_3_s3], [.4.bt2][bt2_grcg6a_4_s3], [.rev.1.bt2][bt2_grcg6a_r1_s3], [.rev.2.bt2][bt2_grcg6a_r2_s3]
Chicken / Galgal4 | [Ensembl][bt2_galgal4_source] | [full zip][bt2_galgal4_full], [.1.bt2][bt2_galgal4_1], [.2.bt2][bt2_galgal4_2], [.3.bt2][bt2_galgal4_3], [.4.bt2][bt2_galgal4_4], [.rev.1.bt2][bt2_galgal4_r1], [.rev.2.bt2][bt2_galgal4_r2] | [full zip][bt2_galgal4_full_s3], [.1.bt2][bt2_galgal4_1_s3], [.2.bt2][bt2_galgal4_2_s3], [.3.bt2][bt2_galgal4_3_s3], [.4.bt2][bt2_galgal4_4_s3], [.rev.1.bt2][bt2_galgal4_r1_s3], [.rev.2.bt2][bt2_galgal4_r2_s3]
Zebrafish / GRCz11 | [NCBI][bt2_grcz11_source] | [full zip][bt2_grcz11_full], [.1.bt2][bt2_grcz11_1], [.2.bt2][bt2_grcz11_2], [.3.bt2][bt2_grcz11_3], [.4.bt2][bt2_grcz11_4], [.rev.1.bt2][bt2_grcz11_r1], [.rev.2.bt2][bt2_grcz11_r2] | [full zip][bt2_grcz11_full_s3], [.1.bt2][bt2_grcz11_1_s3], [.2.bt2][bt2_grcz11_2_s3], [.3.bt2][bt2_grcz11_3_s3], [.4.bt2][bt2_grcz11_4_s3], [.rev.1.bt2][bt2_grcz11_r1_s3], [.rev.2.bt2][bt2_grcz11_r2_s3]
Zebrafish / GRCz10 | [NCBI][bt2_grcz10_source] | [full zip][bt2_grcz10_full], [.1.bt2][bt2_grcz10_1], [.2.bt2][bt2_grcz10_2], [.3.bt2][bt2_grcz10_3], [.4.bt2][bt2_grcz10_4], [.rev.1.bt2][bt2_grcz10_r1], [.rev.2.bt2][bt2_grcz10_r2] | [full zip][bt2_grcz10_full_s3], [.1.bt2][bt2_grcz10_1_s3], [.2.bt2][bt2_grcz10_2_s3], [.3.bt2][bt2_grcz10_3_s3], [.4.bt2][bt2_grcz10_4_s3], [.rev.1.bt2][bt2_grcz10_r1_s3], [.rev.2.bt2][bt2_grcz10_r2_s3]
Corn / AGPv4 | [Ensembl][bt2_agpv4_source] | [full zip][bt2_agpv4_full], [.1.bt2][bt2_agpv4_1], [.2.bt2][bt2_agpv4_2], [.3.bt2][bt2_agpv4_3], [.4.bt2][bt2_agpv4_4], [.rev.1.bt2][bt2_agpv4_r1], [.rev.2.bt2][bt2_agpv4_r2] | [full zip][bt2_agpv4_full_s3], [.1.bt2][bt2_agpv4_1_s3], [.2.bt2][bt2_agpv4_2_s3], [.3.bt2][bt2_agpv4_3_s3], [.4.bt2][bt2_agpv4_4_s3], [.rev.1.bt2][bt2_agpv4_r1_s3], [.rev.2.bt2][bt2_agpv4_r2_s3]
Corn / B73 RefGenV5 | [NCBI][bt2_b73_refgen_v5_source] | [full zip][bt2_b73_refgen_v5_full], [.1.bt2][bt2_b73_refgen_v5_1], [.2.bt2][bt2_b73_refgen_v5_2], [.3.bt2][bt2_b73_refgen_v5_3], [.4.bt2][bt2_b73_refgen_v5_4], [.rev.1.bt2][bt2_b73_refgen_v5_r1], [.rev.2.bt2][bt2_b73_refgen_v5_r2] | [full zip][bt2_b73_refgen_v5_full_s3], [.1.bt2][bt2_b73_refgen_v5_1_s3], [.2.bt2][bt2_b73_refgen_v5_2_s3], [.3.bt2][bt2_b73_refgen_v5_3_s3], [.4.bt2][bt2_b73_refgen_v5_4_s3], [.rev.1.bt2][bt2_b73_refgen_v5_r1_s3], [.rev.2.bt2][bt2_b73_refgen_v5_r2_s3]
Oryza sativa (rice) / Build_4.0 | [NCBI][bt2_build4_source] | [full zip][bt2_build4_full], [.1.bt2][bt2_build4_1], [.2.bt2][bt2_build4_2], [.3.bt2][bt2_build4_3], [.4.bt2][bt2_build4_4], [.rev.1.bt2][bt2_build4_r1], [.rev.2.bt2][bt2_build4_r2] | [full zip][bt2_build4_full_s3], [.1.bt2][bt2_build4_1_s3], [.2.bt2][bt2_build4_2_s3], [.3.bt2][bt2_build4_3_s3], [.4.bt2][bt2_build4_4_s3], [.rev.1.bt2][bt2_build4_r1_s3], [.rev.2.bt2][bt2_build4_r2_s3]
Arabidopsis thaliana / TAIR10 | [Ensembl][bt2_tair10_source] | [full zip][bt2_tair10_full], [.1.bt2][bt2_tair10_1], [.2.bt2][bt2_tair10_2], [.3.bt2][bt2_tair10_3], [.4.bt2][bt2_tair10_4], [.rev.1.bt2][bt2_tair10_r1], [.rev.2.bt2][bt2_tair10_r2] | [full zip][bt2_tair10_full_s3], [.1.bt2][bt2_tair10_1_s3], [.2.bt2][bt2_tair10_2_s3], [.3.bt2][bt2_tair10_3_s3], [.4.bt2][bt2_tair10_4_s3], [.rev.1.bt2][bt2_tair10_r1_s3], [.rev.2.bt2][bt2_tair10_r2_s3]
Fruitfly / BDGP6 | [Ensembl][bt2_bdgp6_source] | [full zip][bt2_bdgp6_full], [.1.bt2][bt2_bdgp6_1], [.2.bt2][bt2_bdgp6_2], [.3.bt2][bt2_bdgp6_3], [.4.bt2][bt2_bdgp6_4], [.rev.1.bt2][bt2_bdgp6_r1], [.rev.2.bt2][bt2_bdgp6_r2] | [full zip][bt2_bdgp6_full_s3], [.1.bt2][bt2_bdgp6_1_s3], [.2.bt2][bt2_bdgp6_2_s3], [.3.bt2][bt2_bdgp6_3_s3], [.4.bt2][bt2_bdgp6_4_s3], [.rev.1.bt2][bt2_bdgp6_r1_s3], [.rev.2.bt2][bt2_bdgp6_r2_s3]
Fruitfly / Dmel A4 1.0 | [NCBI][bt2_dmela410_source] | [full zip][bt2_dmela410_full], [.1.bt2][bt2_dmela410_1], [.2.bt2][bt2_dmela410_2], [.3.bt2][bt2_dmela410_3], [.4.bt2][bt2_dmela410_4], [.rev.1.bt2][bt2_dmela410_r1], [.rev.2.bt2][bt2_dmela410_r2] | [full zip][bt2_dmela410_full_s3], [.1.bt2][bt2_dmela410_1_s3], [.2.bt2][bt2_dmela410_2_s3], [.3.bt2][bt2_dmela410_3_s3], [.4.bt2][bt2_dmela410_4_s3], [.rev.1.bt2][bt2_dmela410_r1_s3], [.rev.2.bt2][bt2_dmela410_r2_s3]
C. elegans / WBcel235 | [Ensembl][bt2_wbcel235_source] | [full zip][bt2_wbcel235_full], [.1.bt2][bt2_wbcel235_1], [.2.bt2][bt2_wbcel235_2], [.3.bt2][bt2_wbcel235_3], [.4.bt2][bt2_wbcel235_4], [.rev.1.bt2][bt2_wbcel235_r1], [.rev.2.bt2][bt2_wbcel235_r2] | [full zip][bt2_wbcel235_full_s3], [.1.bt2][bt2_wbcel235_1_s3], [.2.bt2][bt2_wbcel235_2_s3], [.3.bt2][bt2_wbcel235_3_s3], [.4.bt2][bt2_wbcel235_4_s3], [.rev.1.bt2][bt2_wbcel235_r1_s3], [.rev.2.bt2][bt2_wbcel235_r2_s3]
Yeast / R64-1-1 | [Ensembl][bt2_r6411_source] | [full zip][bt2_r6411_full], [.1.bt2][bt2_r6411_1], [.2.bt2][bt2_r6411_2], [.3.bt2][bt2_r6411_3], [.4.bt2][bt2_r6411_4], [.rev.1.bt2][bt2_r6411_r1], [.rev.2.bt2][bt2_r6411_r2] | [full zip][bt2_r6411_full_s3], [.1.bt2][bt2_r6411_1_s3], [.2.bt2][bt2_r6411_2_s3], [.3.bt2][bt2_r6411_3_s3], [.4.bt2][bt2_r6411_4_s3], [.rev.1.bt2][bt2_r6411_r1_s3], [.rev.2.bt2][bt2_r6411_r2_s3]

<div class="datatable-end"></div>

[1000 Genomes]: https://www.internationalgenome.org
[iGenomes]: https://support.illumina.com/sequencing/sequencing_software/igenome.html

1. Before 10/29/2020, the index posted here erroneously included ALT loci.  This was fixed on 10/29/2020. 
2. Major SNVs determined from [1000 Genomes Project](https://www.internationalgenome.org) variant calls.  [Details here](https://github.com/BenLangmead/bowtie-majref).
3. CHM13 human reference from [Telomere-to-Telomere consortium](https://github.com/nanopore-wgs-consortium/CHM13), plus Y chromosome from GRCh38
4. Ashkenazi reference genome from [10.1186/s13059-020-02047-7](https://doi.org/10.1186/s13059-020-02047-7)

Bowtie and Bowtie 2 are the work of
Ben Langmead,
Cole Trapnell,
Mihai Pop,
Steven Salzberg,
Val Antonescu,
Rone Charles among others.
Please see the [Bowtie] and [Bowtie 2]
websites for more information on the software, authors, and how to cite the work.

[Bowtie]: http://bowtie-bio.sourceforge.net
[Bowtie 2]: http://bowtie-bio.sourceforge.net/bowtie2
[bt2_t2tplusy_source]: https://github.com/nanopore-wgs-consortium/CHM13
[bt2_grch38_noalt_source]: ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/
[bt2_grch38_noalt_decoy_source]: ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.15_GRCh38/seqs_for_alignment_pipelines.ucsc_ids/
[bt2_grch38_1kgmaj_source]: ftp://ftp.ccb.jhu.edu/pub/data/bowtie2_indexes/
[bt2_grch37_source]: https://grch37.ensembl.org/index.html
[bt2_ash1_source]: ftp://ftp.ccb.jhu.edu/pub/data/Homo_sapiens/Ash1/v1.7/Assembly/
[bt2_ash1_2_source]: ftp://ftp.ccb.jhu.edu/pub/data/Homo_sapiens/Ash1/v2.0/Assembly/
[bt2_hg19_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes
[bt2_hg18_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/hg18/chromosomes
[bt2_clintptr2_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/880/755/GCF_002880755.1_Clint_PTRv2/
[bt2_chimp214_source]: https://www.ensembl.org/Pan_troglodytes/Info/Index
[bt2_mmul10_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/003/339/765/GCF_003339765.1_Mmul_10/
[bt2_arsucd12_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/002/263/795/GCF_002263795.1_ARS-UCD1.2/
[bt2_sscorfa111_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/003/025/GCF_000003025.6_Sscrofa11.1/
[bt2_canfam31_source]: https://www.ensembl.org/Canis_lupus_familiaris/Info/Index
[bt2_grcm38_source]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001635.20/
[bt2_grcm39_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/635/GCF_000001635.27_GRCm39/
[bt2_mm10_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/mm10/chromosomes
[bt2_mm9_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/mm9/chromosomes
[bt2_rn4_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/rn4/chromosomes
[bt2_rnor60_source]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001895.5/
[bt2_grcg6a_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/315/GCF_000002315.6_GRCg6a/
[bt2_galgal4_source]: http://jul2016.archive.ensembl.org/Gallus_gallus/Info/Index
[bt2_agpv4_source]: http://plants.ensembl.org/Zea_mays/Info/Index
[bt2_build4_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/425/GCF_000005425.2_Build_4.0/
[bt2_grcz11_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/002/035/GCF_000002035.6_GRCz11/
[bt2_grcz10_source]: https://www.ensembl.org/Drosophila_melanogaster/Info/Index
[bt2_tair10_source]: http://plants.ensembl.org/Arabidopsis_thaliana/Info/Index
[bt2_bdgp6_source]: https://jan2019.archive.ensembl.org/Drosophila_melanogaster/Info/Index
[bt2_wbcel235_source]: https://www.ensembl.org/Caenorhabditis_elegans/Info/Index
[bt2_r6411_source]: https://www.ensembl.org/Saccharomyces_cerevisiae/Info/Index
[bt2_dmela410_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/002/300/595/GCA_002300595.1_Dmel_A4_1.0/
[bt2_b73_refgen_v5_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/902/167/145/GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0/
[bt2_canfam4_source]: https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/002/285/


[bt2_grch38_noalt_full]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.zip
[bt2_grch38_noalt_1]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.1.bt2
[bt2_grch38_noalt_2]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.2.bt2
[bt2_grch38_noalt_3]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.3.bt2
[bt2_grch38_noalt_4]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.4.bt2
[bt2_grch38_noalt_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.rev.1.bt2
[bt2_grch38_noalt_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.rev.2.bt2
[bt2_grch38_noalt_full_s3]: s3://genome-idx/bt/GRCh38_noalt_as.zip
[bt2_grch38_noalt_1_s3]: s3://genome-idx/bt/GRCh38_noalt_as.1.bt2
[bt2_grch38_noalt_2_s3]: s3://genome-idx/bt/GRCh38_noalt_as.2.bt2
[bt2_grch38_noalt_3_s3]: s3://genome-idx/bt/GRCh38_noalt_as.3.bt2
[bt2_grch38_noalt_4_s3]: s3://genome-idx/bt/GRCh38_noalt_as.4.bt2
[bt2_grch38_noalt_r1_s3]: s3://genome-idx/bt/GRCh38_noalt_as.rev.1.bt2
[bt2_grch38_noalt_r2_s3]: s3://genome-idx/bt/GRCh38_noalt_as.rev.2.bt2
[bt2_grch38_noalt_decoy_full]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.zip
[bt2_grch38_noalt_decoy_1]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.1.bt2
[bt2_grch38_noalt_decoy_2]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.2.bt2
[bt2_grch38_noalt_decoy_3]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.3.bt2
[bt2_grch38_noalt_decoy_4]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.4.bt2
[bt2_grch38_noalt_decoy_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.rev.1.bt2
[bt2_grch38_noalt_decoy_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_decoy_as.rev.2.bt2
[bt2_grch38_noalt_decoy_full_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.zip
[bt2_grch38_noalt_decoy_1_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.1.bt2
[bt2_grch38_noalt_decoy_2_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.2.bt2
[bt2_grch38_noalt_decoy_3_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.3.bt2
[bt2_grch38_noalt_decoy_4_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.4.bt2
[bt2_grch38_noalt_decoy_r1_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.rev.1.bt2
[bt2_grch38_noalt_decoy_r2_s3]: s3://genome-idx/bt/GRCh38_noalt_decoy_as.rev.2.bt2
[bt2_grch38_1kgmaj_full]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.zip
[bt2_grch38_1kgmaj_1]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.1.bt2
[bt2_grch38_1kgmaj_2]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.2.bt2
[bt2_grch38_1kgmaj_3]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.3.bt2
[bt2_grch38_1kgmaj_4]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.4.bt2
[bt2_grch38_1kgmaj_r1]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.rev.1.bt2
[bt2_grch38_1kgmaj_r2]: https://genome-idx.s3.amazonaws.com/bt/grch38_1kgmaj.rev.2.bt2
[bt2_grch38_1kgmaj_full_s3]: s3://genome-idx/bt/grch38_1kgmaj.zip
[bt2_grch38_1kgmaj_1_s3]: s3://genome-idx/bt/grch38_1kgmaj.1.bt2
[bt2_grch38_1kgmaj_2_s3]: s3://genome-idx/bt/grch38_1kgmaj.2.bt2
[bt2_grch38_1kgmaj_3_s3]: s3://genome-idx/bt/grch38_1kgmaj.3.bt2
[bt2_grch38_1kgmaj_4_s3]: s3://genome-idx/bt/grch38_1kgmaj.4.bt2
[bt2_grch38_1kgmaj_r1_s3]: s3://genome-idx/bt/grch38_1kgmaj.rev.1.bt2
[bt2_grch38_1kgmaj_r2_s3]: s3://genome-idx/bt/grch38_1kgmaj.rev.2.bt2
[bt2_grch37_full]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.zip
[bt2_grch37_1]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.1.bt2
[bt2_grch37_2]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.2.bt2
[bt2_grch37_3]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.3.bt2
[bt2_grch37_4]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.4.bt2
[bt2_grch37_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.rev.1.bt2
[bt2_grch37_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCh37.rev.2.bt2
[bt2_grch37_full_s3]: s3://genome-idx/bt/GRCh37.zip
[bt2_grch37_1_s3]: s3://genome-idx/bt/GRCh37.1.bt2
[bt2_grch37_2_s3]: s3://genome-idx/bt/GRCh37.2.bt2
[bt2_grch37_3_s3]: s3://genome-idx/bt/GRCh37.3.bt2
[bt2_grch37_4_s3]: s3://genome-idx/bt/GRCh37.4.bt2
[bt2_grch37_r1_s3]: s3://genome-idx/bt/GRCh37.rev.1.bt2
[bt2_grch37_r2_s3]: s3://genome-idx/bt/GRCh37.rev.2.bt2
[bt2_ash1_full]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.zip
[bt2_ash1_1]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.1.bt2
[bt2_ash1_2]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.2.bt2
[bt2_ash1_3]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.3.bt2
[bt2_ash1_4]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.4.bt2
[bt2_ash1_r1]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.rev.1.bt2
[bt2_ash1_r2]: https://genome-idx.s3.amazonaws.com/bt/Ash1v1.7.rev.2.bt2
[bt2_ash1_full_s3]: s3://genome-idx/bt/Ash1v1.7.zip
[bt2_ash1_1_s3]: s3://genome-idx/bt/Ash1v1.7.1.bt2
[bt2_ash1_2_s3]: s3://genome-idx/bt/Ash1v1.7.2.bt2
[bt2_ash1_3_s3]: s3://genome-idx/bt/Ash1v1.7.3.bt2
[bt2_ash1_4_s3]: s3://genome-idx/bt/Ash1v1.7.4.bt2
[bt2_ash1_r1_s3]: s3://genome-idx/bt/Ash1v1.7.rev.1.bt2
[bt2_ash1_r2_s3]: s3://genome-idx/bt/Ash1v1.7.rev.2.bt2
[bt2_ash1_2_full]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.zip
[bt2_ash1_2_1]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.1.bt2
[bt2_ash1_2_2]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.2.bt2
[bt2_ash1_2_3]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.3.bt2
[bt2_ash1_2_4]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.4.bt2
[bt2_ash1_2_r1]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.rev.1.bt2
[bt2_ash1_2_r2]: https://genome-idx.s3.amazonaws.com/bt/Ash1_v2.0.rev.2.bt2
[bt2_ash1_2_full_s3]: s3://genome-idx/bt/Ash1_v2.0.zip
[bt2_ash1_2_1_s3]: s3://genome-idx/bt/Ash1_v2.0.1.bt2
[bt2_ash1_2_2_s3]: s3://genome-idx/bt/Ash1_v2.0.2.bt2
[bt2_ash1_2_3_s3]: s3://genome-idx/bt/Ash1_v2.0.3.bt2
[bt2_ash1_2_4_s3]: s3://genome-idx/bt/Ash1_v2.0.4.bt2
[bt2_ash1_2_r1_s3]: s3://genome-idx/bt/Ash1_v2.0.rev.1.bt2
[bt2_ash1_2_r2_s3]: s3://genome-idx/bt/Ash1_v2.0.rev.2.bt2
[bt2_t2tplusy_full]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.zip
[bt2_t2tplusy_1]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.1.bt2
[bt2_t2tplusy_2]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.2.bt2
[bt2_t2tplusy_3]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.3.bt2
[bt2_t2tplusy_4]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.4.bt2
[bt2_t2tplusy_r1]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.rev.1.bt2
[bt2_t2tplusy_r2]: https://genome-idx.s3.amazonaws.com/bt/chm13.draft_v1.0_plusY.rev.2.bt2
[bt2_t2tplusy_full_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.zip
[bt2_t2tplusy_1_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.1.bt2
[bt2_t2tplusy_2_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.2.bt2
[bt2_t2tplusy_3_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.3.bt2
[bt2_t2tplusy_4_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.4.bt2
[bt2_t2tplusy_r1_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.rev.1.bt2
[bt2_t2tplusy_r2_s3]: s3://genome-idx/bt/chm13.draft_v1.0_plusY.rev.2.bt2
[bt2_hg19_full]: https://genome-idx.s3.amazonaws.com/bt/hg19.zip
[bt2_hg19_1]: https://genome-idx.s3.amazonaws.com/bt/hg19.1.bt2
[bt2_hg19_2]: https://genome-idx.s3.amazonaws.com/bt/hg19.2.bt2
[bt2_hg19_3]: https://genome-idx.s3.amazonaws.com/bt/hg19.3.bt2
[bt2_hg19_4]: https://genome-idx.s3.amazonaws.com/bt/hg19.4.bt2
[bt2_hg19_r1]: https://genome-idx.s3.amazonaws.com/bt/hg19.rev.1.bt2
[bt2_hg19_r2]: https://genome-idx.s3.amazonaws.com/bt/hg19.rev.2.bt2
[bt2_hg19_full_s3]: s3://genome-idx/bt/hg19.zip
[bt2_hg19_1_s3]: s3://genome-idx/bt/hg19.1.bt2
[bt2_hg19_2_s3]: s3://genome-idx/bt/hg19.2.bt2
[bt2_hg19_3_s3]: s3://genome-idx/bt/hg19.3.bt2
[bt2_hg19_4_s3]: s3://genome-idx/bt/hg19.4.bt2
[bt2_hg19_r1_s3]: s3://genome-idx/bt/hg19.rev.1.bt2
[bt2_hg19_r2_s3]: s3://genome-idx/bt/hg19.rev.2.bt2
[bt2_hg18_full]: https://genome-idx.s3.amazonaws.com/bt/hg18.zip
[bt2_hg18_1]: https://genome-idx.s3.amazonaws.com/bt/hg18.1.bt2
[bt2_hg18_2]: https://genome-idx.s3.amazonaws.com/bt/hg18.2.bt2
[bt2_hg18_3]: https://genome-idx.s3.amazonaws.com/bt/hg18.3.bt2
[bt2_hg18_4]: https://genome-idx.s3.amazonaws.com/bt/hg18.4.bt2
[bt2_hg18_r1]: https://genome-idx.s3.amazonaws.com/bt/hg18.rev.1.bt2
[bt2_hg18_r2]: https://genome-idx.s3.amazonaws.com/bt/hg18.rev.2.bt2
[bt2_hg18_full_s3]: s3://genome-idx/bt/hg18.zip
[bt2_hg18_1_s3]: s3://genome-idx/bt/hg18.1.bt2
[bt2_hg18_2_s3]: s3://genome-idx/bt/hg18.2.bt2
[bt2_hg18_3_s3]: s3://genome-idx/bt/hg18.3.bt2
[bt2_hg18_4_s3]: s3://genome-idx/bt/hg18.4.bt2
[bt2_hg18_r1_s3]: s3://genome-idx/bt/hg18.rev.1.bt2
[bt2_hg18_r2_s3]: s3://genome-idx/bt/hg18.rev.2.bt2
[bt2_grcm38_full]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.zip
[bt2_grcm38_1]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.1.bt2
[bt2_grcm38_2]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.2.bt2
[bt2_grcm38_3]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.3.bt2
[bt2_grcm38_4]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.4.bt2
[bt2_grcm38_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.rev.1.bt2
[bt2_grcm38_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCm38.rev.2.bt2
[bt2_grcm38_full_s3]: s3://genome-idx/bt/GRCm38.zip
[bt2_grcm38_1_s3]: s3://genome-idx/bt/GRCm38.1.bt2
[bt2_grcm38_2_s3]: s3://genome-idx/bt/GRCm38.2.bt2
[bt2_grcm38_3_s3]: s3://genome-idx/bt/GRCm38.3.bt2
[bt2_grcm38_4_s3]: s3://genome-idx/bt/GRCm38.4.bt2
[bt2_grcm38_r1_s3]: s3://genome-idx/bt/GRCm38.rev.1.bt2
[bt2_grcm38_r2_s3]: s3://genome-idx/bt/GRCm38.rev.2.bt2
[bt2_grcm39_full]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.zip
[bt2_grcm39_1]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.1.bt2
[bt2_grcm39_2]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.2.bt2
[bt2_grcm39_3]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.3.bt2
[bt2_grcm39_4]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.4.bt2
[bt2_grcm39_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.rev.1.bt2
[bt2_grcm39_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCm39.rev.2.bt2
[bt2_grcm39_full_s3]: s3://genome-idx/bt/GRCm39.zip
[bt2_grcm39_1_s3]: s3://genome-idx/bt/GRCm39.1.bt2
[bt2_grcm39_2_s3]: s3://genome-idx/bt/GRCm39.2.bt2
[bt2_grcm39_3_s3]: s3://genome-idx/bt/GRCm39.3.bt2
[bt2_grcm39_4_s3]: s3://genome-idx/bt/GRCm39.4.bt2
[bt2_grcm39_r1_s3]: s3://genome-idx/bt/GRCm39.rev.1.bt2
[bt2_grcm39_r2_s3]: s3://genome-idx/bt/GRCm39.rev.2.bt2
[bt2_mm10_full]: https://genome-idx.s3.amazonaws.com/bt/mm10.zip
[bt2_mm10_1]: https://genome-idx.s3.amazonaws.com/bt/mm10.1.bt2
[bt2_mm10_2]: https://genome-idx.s3.amazonaws.com/bt/mm10.2.bt2
[bt2_mm10_3]: https://genome-idx.s3.amazonaws.com/bt/mm10.3.bt2
[bt2_mm10_4]: https://genome-idx.s3.amazonaws.com/bt/mm10.4.bt2
[bt2_mm10_r1]: https://genome-idx.s3.amazonaws.com/bt/mm10.rev.1.bt2
[bt2_mm10_r2]: https://genome-idx.s3.amazonaws.com/bt/mm10.rev.2.bt2
[bt2_mm10_full_s3]: s3://genome-idx/bt/mm10.zip
[bt2_mm10_1_s3]: s3://genome-idx/bt/mm10.1.bt2
[bt2_mm10_2_s3]: s3://genome-idx/bt/mm10.2.bt2
[bt2_mm10_3_s3]: s3://genome-idx/bt/mm10.3.bt2
[bt2_mm10_4_s3]: s3://genome-idx/bt/mm10.4.bt2
[bt2_mm10_r1_s3]: s3://genome-idx/bt/mm10.rev.1.bt2
[bt2_mm10_r2_s3]: s3://genome-idx/bt/mm10.rev.2.bt2
[bt2_mm9_full]: https://genome-idx.s3.amazonaws.com/bt/mm9.zip
[bt2_mm9_1]: https://genome-idx.s3.amazonaws.com/bt/mm9.1.bt2
[bt2_mm9_2]: https://genome-idx.s3.amazonaws.com/bt/mm9.2.bt2
[bt2_mm9_3]: https://genome-idx.s3.amazonaws.com/bt/mm9.3.bt2
[bt2_mm9_4]: https://genome-idx.s3.amazonaws.com/bt/mm9.4.bt2
[bt2_mm9_r1]: https://genome-idx.s3.amazonaws.com/bt/mm9.rev.1.bt2
[bt2_mm9_r2]: https://genome-idx.s3.amazonaws.com/bt/mm9.rev.2.bt2
[bt2_mm9_full_s3]: s3://genome-idx/bt/mm9.zip
[bt2_mm9_1_s3]: s3://genome-idx/bt/mm9.1.bt2
[bt2_mm9_2_s3]: s3://genome-idx/bt/mm9.2.bt2
[bt2_mm9_3_s3]: s3://genome-idx/bt/mm9.3.bt2
[bt2_mm9_4_s3]: s3://genome-idx/bt/mm9.4.bt2
[bt2_mm9_r1_s3]: s3://genome-idx/bt/mm9.rev.1.bt2
[bt2_mm9_r2_s3]: s3://genome-idx/bt/mm9.rev.2.bt2
[bt2_clintptr2_full]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.zip
[bt2_clintptr2_1]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.1.bt2
[bt2_clintptr2_2]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.2.bt2
[bt2_clintptr2_3]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.3.bt2
[bt2_clintptr2_4]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.4.bt2
[bt2_clintptr2_r1]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.rev.1.bt2
[bt2_clintptr2_r2]: https://genome-idx.s3.amazonaws.com/bt/Clint_PTRv2.rev.2.bt2
[bt2_clintptr2_full_s3]: s3://genome-idx/bt/Clint_PTRv2.zip
[bt2_clintptr2_1_s3]: s3://genome-idx/bt/Clint_PTRv2.1.bt2
[bt2_clintptr2_2_s3]: s3://genome-idx/bt/Clint_PTRv2.2.bt2
[bt2_clintptr2_3_s3]: s3://genome-idx/bt/Clint_PTRv2.3.bt2
[bt2_clintptr2_4_s3]: s3://genome-idx/bt/Clint_PTRv2.4.bt2
[bt2_clintptr2_r1_s3]: s3://genome-idx/bt/Clint_PTRv2.rev.1.bt2
[bt2_clintptr2_r2_s3]: s3://genome-idx/bt/Clint_PTRv2.rev.2.bt2
[bt2_chimp214_full]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.zip
[bt2_chimp214_1]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.1.bt2
[bt2_chimp214_2]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.2.bt2
[bt2_chimp214_3]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.3.bt2
[bt2_chimp214_4]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.4.bt2
[bt2_chimp214_r1]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.rev.1.bt2
[bt2_chimp214_r2]: https://genome-idx.s3.amazonaws.com/bt/CHIMP2.1.4.rev.2.bt2
[bt2_chimp214_full_s3]: s3://genome-idx/bt/CHIMP2.1.4.zip
[bt2_chimp214_1_s3]: s3://genome-idx/bt/CHIMP2.1.4.1.bt2
[bt2_chimp214_2_s3]: s3://genome-idx/bt/CHIMP2.1.4.2.bt2
[bt2_chimp214_3_s3]: s3://genome-idx/bt/CHIMP2.1.4.3.bt2
[bt2_chimp214_4_s3]: s3://genome-idx/bt/CHIMP2.1.4.4.bt2
[bt2_chimp214_r1_s3]: s3://genome-idx/bt/CHIMP2.1.4.rev.1.bt2
[bt2_chimp214_r2_s3]: s3://genome-idx/bt/CHIMP2.1.4.rev.2.bt2
[bt2_mmul10_full]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.zip
[bt2_mmul10_1]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.1.bt2
[bt2_mmul10_2]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.2.bt2
[bt2_mmul10_3]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.3.bt2
[bt2_mmul10_4]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.4.bt2
[bt2_mmul10_r1]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.rev.1.bt2
[bt2_mmul10_r2]: https://genome-idx.s3.amazonaws.com/bt/Mmul_10.rev.2.bt2
[bt2_mmul10_full_s3]: s3://genome-idx/bt/Mmul_10.zip
[bt2_mmul10_1_s3]: s3://genome-idx/bt/Mmul_10.1.bt2
[bt2_mmul10_2_s3]: s3://genome-idx/bt/Mmul_10.2.bt2
[bt2_mmul10_3_s3]: s3://genome-idx/bt/Mmul_10.3.bt2
[bt2_mmul10_4_s3]: s3://genome-idx/bt/Mmul_10.4.bt2
[bt2_mmul10_r1_s3]: s3://genome-idx/bt/Mmul_10.rev.1.bt2
[bt2_mmul10_r2_s3]: s3://genome-idx/bt/Mmul_10.rev.2.bt2
[bt2_arsucd12_full]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.zip
[bt2_arsucd12_1]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.1.bt2
[bt2_arsucd12_2]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.2.bt2
[bt2_arsucd12_3]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.3.bt2
[bt2_arsucd12_4]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.4.bt2
[bt2_arsucd12_r1]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.rev.1.bt2
[bt2_arsucd12_r2]: https://genome-idx.s3.amazonaws.com/bt/ARS-UCD1.2.rev.2.bt2
[bt2_arsucd12_full_s3]: s3://genome-idx/bt/ARS-UCD1.2.zip
[bt2_arsucd12_1_s3]: s3://genome-idx/bt/ARS-UCD1.2.1.bt2
[bt2_arsucd12_2_s3]: s3://genome-idx/bt/ARS-UCD1.2.2.bt2
[bt2_arsucd12_3_s3]: s3://genome-idx/bt/ARS-UCD1.2.3.bt2
[bt2_arsucd12_4_s3]: s3://genome-idx/bt/ARS-UCD1.2.4.bt2
[bt2_arsucd12_r1_s3]: s3://genome-idx/bt/ARS-UCD1.2.rev.1.bt2
[bt2_arsucd12_r2_s3]: s3://genome-idx/bt/ARS-UCD1.2.rev.2.bt2
[bt2_sscorfa111_full]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.zip
[bt2_sscorfa111_1]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.1.bt2
[bt2_sscorfa111_2]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.2.bt2
[bt2_sscorfa111_3]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.3.bt2
[bt2_sscorfa111_4]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.4.bt2
[bt2_sscorfa111_r1]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.rev.1.bt2
[bt2_sscorfa111_r2]: https://genome-idx.s3.amazonaws.com/bt/Sscrofa11.1.rev.2.bt2
[bt2_sscorfa111_full_s3]: s3://genome-idx/bt/Sscrofa11.1.zip
[bt2_sscorfa111_1_s3]: s3://genome-idx/bt/Sscrofa11.1.1.bt2
[bt2_sscorfa111_2_s3]: s3://genome-idx/bt/Sscrofa11.1.2.bt2
[bt2_sscorfa111_3_s3]: s3://genome-idx/bt/Sscrofa11.1.3.bt2
[bt2_sscorfa111_4_s3]: s3://genome-idx/bt/Sscrofa11.1.4.bt2
[bt2_sscorfa111_r1_s3]: s3://genome-idx/bt/Sscrofa11.1.rev.1.bt2
[bt2_sscorfa111_r2_s3]: s3://genome-idx/bt/Sscrofa11.1.rev.2.bt2
[bt2_canfam31_full]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.zip
[bt2_canfam31_1]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.1.bt2
[bt2_canfam31_2]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.2.bt2
[bt2_canfam31_3]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.3.bt2
[bt2_canfam31_4]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.4.bt2
[bt2_canfam31_r1]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.rev.1.bt2
[bt2_canfam31_r2]: https://genome-idx.s3.amazonaws.com/bt/CanFam3.1.rev.2.bt2
[bt2_canfam31_full_s3]: s3://genome-idx/bt/CanFam3.1.zip
[bt2_canfam31_1_s3]: s3://genome-idx/bt/CanFam3.1.1.bt2
[bt2_canfam31_2_s3]: s3://genome-idx/bt/CanFam3.1.2.bt2
[bt2_canfam31_3_s3]: s3://genome-idx/bt/CanFam3.1.3.bt2
[bt2_canfam31_4_s3]: s3://genome-idx/bt/CanFam3.1.4.bt2
[bt2_canfam31_r1_s3]: s3://genome-idx/bt/CanFam3.1.rev.1.bt2
[bt2_canfam31_r2_s3]: s3://genome-idx/bt/CanFam3.1.rev.2.bt2
[bt2_canfam4_full]: https://genome-idx.s3.amazonaws.com/bt/canfam4.zip
[bt2_canfam4_1]: https://genome-idx.s3.amazonaws.com/bt/canfam4.1.bt2
[bt2_canfam4_2]: https://genome-idx.s3.amazonaws.com/bt/canfam4.2.bt2
[bt2_canfam4_3]: https://genome-idx.s3.amazonaws.com/bt/canfam4.3.bt2
[bt2_canfam4_4]: https://genome-idx.s3.amazonaws.com/bt/canfam4.4.bt2
[bt2_canfam4_r1]: https://genome-idx.s3.amazonaws.com/bt/canfam4.rev.1.bt2
[bt2_canfam4_r2]: https://genome-idx.s3.amazonaws.com/bt/canfam4.rev.2.bt2
[bt2_canfam4_full_s3]: s3://genome-idx/bt/canfam4.zip
[bt2_canfam4_1_s3]: s3://genome-idx/bt/canfam4.1.bt2
[bt2_canfam4_2_s3]: s3://genome-idx/bt/canfam4.2.bt2
[bt2_canfam4_3_s3]: s3://genome-idx/bt/canfam4.3.bt2
[bt2_canfam4_4_s3]: s3://genome-idx/bt/canfam4.4.bt2
[bt2_canfam4_r1_s3]: s3://genome-idx/bt/canfam4.rev.1.bt2
[bt2_canfam4_r2_s3]: s3://genome-idx/bt/canfam4.rev.2.bt2
[bt2_rn4_full]: https://genome-idx.s3.amazonaws.com/bt/rn4.zip
[bt2_rn4_1]: https://genome-idx.s3.amazonaws.com/bt/rn4.1.bt2
[bt2_rn4_2]: https://genome-idx.s3.amazonaws.com/bt/rn4.2.bt2
[bt2_rn4_3]: https://genome-idx.s3.amazonaws.com/bt/rn4.3.bt2
[bt2_rn4_4]: https://genome-idx.s3.amazonaws.com/bt/rn4.4.bt2
[bt2_rn4_r1]: https://genome-idx.s3.amazonaws.com/bt/rn4.rev.1.bt2
[bt2_rn4_r2]: https://genome-idx.s3.amazonaws.com/bt/rn4.rev.2.bt2
[bt2_rn4_full_s3]: s3://genome-idx/bt/rn4.zip
[bt2_rn4_1_s3]: s3://genome-idx/bt/rn4.1.bt2
[bt2_rn4_2_s3]: s3://genome-idx/bt/rn4.2.bt2
[bt2_rn4_3_s3]: s3://genome-idx/bt/rn4.3.bt2
[bt2_rn4_4_s3]: s3://genome-idx/bt/rn4.4.bt2
[bt2_rn4_r1_s3]: s3://genome-idx/bt/rn4.rev.1.bt2
[bt2_rn4_r2_s3]: s3://genome-idx/bt/rn4.rev.2.bt2
[bt2_rnor60_full]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.zip
[bt2_rnor60_1]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.1.bt2
[bt2_rnor60_2]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.2.bt2
[bt2_rnor60_3]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.3.bt2
[bt2_rnor60_4]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.4.bt2
[bt2_rnor60_r1]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.rev.1.bt2
[bt2_rnor60_r2]: https://genome-idx.s3.amazonaws.com/bt/Rnor_6.0.rev.2.bt2
[bt2_rnor60_full_s3]: s3://genome-idx/bt/Rnor_6.0.zip
[bt2_rnor60_1_s3]: s3://genome-idx/bt/Rnor_6.0.1.bt2
[bt2_rnor60_2_s3]: s3://genome-idx/bt/Rnor_6.0.2.bt2
[bt2_rnor60_3_s3]: s3://genome-idx/bt/Rnor_6.0.3.bt2
[bt2_rnor60_4_s3]: s3://genome-idx/bt/Rnor_6.0.4.bt2
[bt2_rnor60_r1_s3]: s3://genome-idx/bt/Rnor_6.0.rev.1.bt2
[bt2_rnor60_r2_s3]: s3://genome-idx/bt/Rnor_6.0.rev.2.bt2
[bt2_grcg6a_full]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.zip
[bt2_grcg6a_1]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.1.bt2
[bt2_grcg6a_2]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.2.bt2
[bt2_grcg6a_3]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.3.bt2
[bt2_grcg6a_4]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.4.bt2
[bt2_grcg6a_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.rev.1.bt2
[bt2_grcg6a_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCg6a.rev.2.bt2
[bt2_grcg6a_full_s3]: s3://genome-idx/bt/GRCg6a.zip
[bt2_grcg6a_1_s3]: s3://genome-idx/bt/GRCg6a.1.bt2
[bt2_grcg6a_2_s3]: s3://genome-idx/bt/GRCg6a.2.bt2
[bt2_grcg6a_3_s3]: s3://genome-idx/bt/GRCg6a.3.bt2
[bt2_grcg6a_4_s3]: s3://genome-idx/bt/GRCg6a.4.bt2
[bt2_grcg6a_r1_s3]: s3://genome-idx/bt/GRCg6a.rev.1.bt2
[bt2_grcg6a_r2_s3]: s3://genome-idx/bt/GRCg6a.rev.2.bt2
[bt2_galgal4_full]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.zip
[bt2_galgal4_1]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.1.bt2
[bt2_galgal4_2]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.2.bt2
[bt2_galgal4_3]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.3.bt2
[bt2_galgal4_4]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.4.bt2
[bt2_galgal4_r1]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.rev.1.bt2
[bt2_galgal4_r2]: https://genome-idx.s3.amazonaws.com/bt/Galgal4.rev.2.bt2
[bt2_galgal4_full_s3]: s3://genome-idx/bt/Galgal4.zip
[bt2_galgal4_1_s3]: s3://genome-idx/bt/Galgal4.1.bt2
[bt2_galgal4_2_s3]: s3://genome-idx/bt/Galgal4.2.bt2
[bt2_galgal4_3_s3]: s3://genome-idx/bt/Galgal4.3.bt2
[bt2_galgal4_4_s3]: s3://genome-idx/bt/Galgal4.4.bt2
[bt2_galgal4_r1_s3]: s3://genome-idx/bt/Galgal4.rev.1.bt2
[bt2_galgal4_r2_s3]: s3://genome-idx/bt/Galgal4.rev.2.bt2
[bt2_grcz11_full]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.zip
[bt2_grcz11_1]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.1.bt2
[bt2_grcz11_2]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.2.bt2
[bt2_grcz11_3]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.3.bt2
[bt2_grcz11_4]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.4.bt2
[bt2_grcz11_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.rev.1.bt2
[bt2_grcz11_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCz11.rev.2.bt2
[bt2_grcz11_full_s3]: s3://genome-idx/bt/GRCz11.zip
[bt2_grcz11_1_s3]: s3://genome-idx/bt/GRCz11.1.bt2
[bt2_grcz11_2_s3]: s3://genome-idx/bt/GRCz11.2.bt2
[bt2_grcz11_3_s3]: s3://genome-idx/bt/GRCz11.3.bt2
[bt2_grcz11_4_s3]: s3://genome-idx/bt/GRCz11.4.bt2
[bt2_grcz11_r1_s3]: s3://genome-idx/bt/GRCz11.rev.1.bt2
[bt2_grcz11_r2_s3]: s3://genome-idx/bt/GRCz11.rev.2.bt2
[bt2_grcz10_full]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.zip
[bt2_grcz10_1]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.1.bt2
[bt2_grcz10_2]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.2.bt2
[bt2_grcz10_3]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.3.bt2
[bt2_grcz10_4]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.4.bt2
[bt2_grcz10_r1]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.rev.1.bt2
[bt2_grcz10_r2]: https://genome-idx.s3.amazonaws.com/bt/GRCz10.rev.2.bt2
[bt2_grcz10_full_s3]: s3://genome-idx/bt/GRCz10.zip
[bt2_grcz10_1_s3]: s3://genome-idx/bt/GRCz10.1.bt2
[bt2_grcz10_2_s3]: s3://genome-idx/bt/GRCz10.2.bt2
[bt2_grcz10_3_s3]: s3://genome-idx/bt/GRCz10.3.bt2
[bt2_grcz10_4_s3]: s3://genome-idx/bt/GRCz10.4.bt2
[bt2_grcz10_r1_s3]: s3://genome-idx/bt/GRCz10.rev.1.bt2
[bt2_grcz10_r2_s3]: s3://genome-idx/bt/GRCz10.rev.2.bt2
[bt2_agpv4_full]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.zip
[bt2_agpv4_1]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.1.bt2
[bt2_agpv4_2]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.2.bt2
[bt2_agpv4_3]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.3.bt2
[bt2_agpv4_4]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.4.bt2
[bt2_agpv4_r1]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.rev.1.bt2
[bt2_agpv4_r2]: https://genome-idx.s3.amazonaws.com/bt/AGPv4.rev.2.bt2
[bt2_agpv4_full_s3]: s3://genome-idx/bt/AGPv4.zip
[bt2_agpv4_1_s3]: s3://genome-idx/bt/AGPv4.1.bt2
[bt2_agpv4_2_s3]: s3://genome-idx/bt/AGPv4.2.bt2
[bt2_agpv4_3_s3]: s3://genome-idx/bt/AGPv4.3.bt2
[bt2_agpv4_4_s3]: s3://genome-idx/bt/AGPv4.4.bt2
[bt2_agpv4_r1_s3]: s3://genome-idx/bt/AGPv4.rev.1.bt2
[bt2_agpv4_r2_s3]: s3://genome-idx/bt/AGPv4.rev.2.bt2
[bt2_b73_refgen_v5_full]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.zip
[bt2_b73_refgen_v5_1]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.1.bt2
[bt2_b73_refgen_v5_2]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.2.bt2
[bt2_b73_refgen_v5_3]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.3.bt2
[bt2_b73_refgen_v5_4]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.4.bt2
[bt2_b73_refgen_v5_r1]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.rev.1.bt2
[bt2_b73_refgen_v5_r2]: https://genome-idx.s3.amazonaws.com/bt/Zm-B73-REFERENCE-NAM-5.0.rev.2.bt2
[bt2_b73_refgen_v5_full_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.zip
[bt2_b73_refgen_v5_1_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.1.bt2
[bt2_b73_refgen_v5_2_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.2.bt2
[bt2_b73_refgen_v5_3_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.3.bt2
[bt2_b73_refgen_v5_4_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.4.bt2
[bt2_b73_refgen_v5_r1_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.rev.1.bt2
[bt2_b73_refgen_v5_r2_s3]: s3://genome-idx/bt/Zm-B73-REFERENCE-NAM-5.0.rev.2.bt2
[bt2_build4_full]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.zip
[bt2_build4_1]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.1.bt2
[bt2_build4_2]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.2.bt2
[bt2_build4_3]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.3.bt2
[bt2_build4_4]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.4.bt2
[bt2_build4_r1]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.rev.1.bt2
[bt2_build4_r2]: https://genome-idx.s3.amazonaws.com/bt/Build_4.0.rev.2.bt2
[bt2_build4_full_s3]: s3://genome-idx/bt/Build_4.0.zip
[bt2_build4_1_s3]: s3://genome-idx/bt/Build_4.0.1.bt2
[bt2_build4_2_s3]: s3://genome-idx/bt/Build_4.0.2.bt2
[bt2_build4_3_s3]: s3://genome-idx/bt/Build_4.0.3.bt2
[bt2_build4_4_s3]: s3://genome-idx/bt/Build_4.0.4.bt2
[bt2_build4_r1_s3]: s3://genome-idx/bt/Build_4.0.rev.1.bt2
[bt2_build4_r2_s3]: s3://genome-idx/bt/Build_4.0.rev.2.bt2
[bt2_tair10_full]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.zip
[bt2_tair10_1]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.1.bt2
[bt2_tair10_2]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.2.bt2
[bt2_tair10_3]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.3.bt2
[bt2_tair10_4]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.4.bt2
[bt2_tair10_r1]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.rev.1.bt2
[bt2_tair10_r2]: https://genome-idx.s3.amazonaws.com/bt/TAIR10.rev.2.bt2
[bt2_tair10_full_s3]: s3://genome-idx/bt/TAIR10.zip
[bt2_tair10_1_s3]: s3://genome-idx/bt/TAIR10.1.bt2
[bt2_tair10_2_s3]: s3://genome-idx/bt/TAIR10.2.bt2
[bt2_tair10_3_s3]: s3://genome-idx/bt/TAIR10.3.bt2
[bt2_tair10_4_s3]: s3://genome-idx/bt/TAIR10.4.bt2
[bt2_tair10_r1_s3]: s3://genome-idx/bt/TAIR10.rev.1.bt2
[bt2_tair10_r2_s3]: s3://genome-idx/bt/TAIR10.rev.2.bt2
[bt2_bdgp6_full]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.zip
[bt2_bdgp6_1]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.1.bt2
[bt2_bdgp6_2]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.2.bt2
[bt2_bdgp6_3]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.3.bt2
[bt2_bdgp6_4]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.4.bt2
[bt2_bdgp6_r1]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.rev.1.bt2
[bt2_bdgp6_r2]: https://genome-idx.s3.amazonaws.com/bt/BDGP6.rev.2.bt2
[bt2_bdgp6_full_s3]: s3://genome-idx/bt/BDGP6.zip
[bt2_bdgp6_1_s3]: s3://genome-idx/bt/BDGP6.1.bt2
[bt2_bdgp6_2_s3]: s3://genome-idx/bt/BDGP6.2.bt2
[bt2_bdgp6_3_s3]: s3://genome-idx/bt/BDGP6.3.bt2
[bt2_bdgp6_4_s3]: s3://genome-idx/bt/BDGP6.4.bt2
[bt2_bdgp6_r1_s3]: s3://genome-idx/bt/BDGP6.rev.1.bt2
[bt2_bdgp6_r2_s3]: s3://genome-idx/bt/BDGP6.rev.2.bt2
[bt2_wbcel235_full]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.zip
[bt2_wbcel235_1]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.1.bt2
[bt2_wbcel235_2]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.2.bt2
[bt2_wbcel235_3]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.3.bt2
[bt2_wbcel235_4]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.4.bt2
[bt2_wbcel235_r1]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.rev.1.bt2
[bt2_wbcel235_r2]: https://genome-idx.s3.amazonaws.com/bt/WBcel235.rev.2.bt2
[bt2_wbcel235_full_s3]: s3://genome-idx/bt/WBcel235.zip
[bt2_wbcel235_1_s3]: s3://genome-idx/bt/WBcel235.1.bt2
[bt2_wbcel235_2_s3]: s3://genome-idx/bt/WBcel235.2.bt2
[bt2_wbcel235_3_s3]: s3://genome-idx/bt/WBcel235.3.bt2
[bt2_wbcel235_4_s3]: s3://genome-idx/bt/WBcel235.4.bt2
[bt2_wbcel235_r1_s3]: s3://genome-idx/bt/WBcel235.rev.1.bt2
[bt2_wbcel235_r2_s3]: s3://genome-idx/bt/WBcel235.rev.2.bt2
[bt2_r6411_full]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.zip
[bt2_r6411_1]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.1.bt2
[bt2_r6411_2]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.2.bt2
[bt2_r6411_3]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.3.bt2
[bt2_r6411_4]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.4.bt2
[bt2_r6411_r1]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.rev.1.bt2
[bt2_r6411_r2]: https://genome-idx.s3.amazonaws.com/bt/R64-1-1.rev.2.bt2
[bt2_r6411_full_s3]: s3://genome-idx/bt/R64-1-1.zip
[bt2_r6411_1_s3]: s3://genome-idx/bt/R64-1-1.1.bt2
[bt2_r6411_2_s3]: s3://genome-idx/bt/R64-1-1.2.bt2
[bt2_r6411_3_s3]: s3://genome-idx/bt/R64-1-1.3.bt2
[bt2_r6411_4_s3]: s3://genome-idx/bt/R64-1-1.4.bt2
[bt2_r6411_r1_s3]: s3://genome-idx/bt/R64-1-1.rev.1.bt2
[bt2_r6411_r2_s3]: s3://genome-idx/bt/R64-1-1.rev.2.bt2
[bt2_dmela410_full]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.zip
[bt2_dmela410_1]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.1.bt2
[bt2_dmela410_2]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.2.bt2
[bt2_dmela410_3]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.3.bt2
[bt2_dmela410_4]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.4.bt2
[bt2_dmela410_r1]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.rev.1.bt2
[bt2_dmela410_r2]: https://genome-idx.s3.amazonaws.com/bt/Dmel_A4_1.0.rev.2.bt2
[bt2_dmela410_full_s3]: s3://genome-idx/bt/Dmel_A4_1.0.zip
[bt2_dmela410_1_s3]: s3://genome-idx/bt/Dmel_A4_1.0.1.bt2
[bt2_dmela410_2_s3]: s3://genome-idx/bt/Dmel_A4_1.0.2.bt2
[bt2_dmela410_3_s3]: s3://genome-idx/bt/Dmel_A4_1.0.3.bt2
[bt2_dmela410_4_s3]: s3://genome-idx/bt/Dmel_A4_1.0.4.bt2
[bt2_dmela410_r1_s3]: s3://genome-idx/bt/Dmel_A4_1.0.rev.1.bt2
[bt2_dmela410_r2_s3]: s3://genome-idx/bt/Dmel_A4_1.0.rev.2.bt2
