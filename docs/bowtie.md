# Bowtie 2 indexes

[Bowtie](http://bowtie-bio.sourceforge.net) and [Bowtie 2](http://bowtie-bio.sourceforge.net/bowtie2) are read aligners for sequencing reads.  Bowtie specializes in short reads, generally about 50bp or shorter.  Bowtie 2 specializes in longer reads, up to around hundreds of base pairs.

In the past, Bowtie 1 & 2 had incompatible genome indexes.  This changed in July 2019 when Bowtie v1.2.3 gained the ability to use Bowtie 2 formatted genome indexes (ending in `.bt2`).  We list only Bowtie 2-format `.bt2` index files here.

See [Bowtie manual](http://bowtie-bio.sourceforge.net/manual.shtml) and [Bowtie 2 manual](http://bowtie-bio.sourceforge.net/bowtie2/manual.shtml) for further details.

Note: all links are placeholders for now.  They will be replaced when the public repo is available.

<div class="datatable-begin"></div>

Species/Build                             | Source                                            | Files                                                                                                                                                                                                                                     
----------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Human / GRCh38                            | [NCBI][bt2_GRCh38_source]                         | [full zip][bt2_GRCh38_full], [.1.bt2][bt2_GRCh38_1], [.2.bt2][bt2_GRCh38_2], [.3.bt2][bt2_GRCh38_3], [.4.bt2][bt2_GRCh38_4], [.rev.1.bt2][bt2_GRCh38_r1], [.rev.2.bt2][bt2_GRCh38_r2]
Human / GRCh38 + major SNVs <sup>1</sup>  | [NCBI][bt2_grch38_1kgmaj_source] + [1000 Genomes] | [full zip][bt2_grch38_1kgmaj_full], [.1.bt2][bt2_grch38_1kgmaj_1], [.2.bt2][bt2_grch38_1kgmaj_2], [.3.bt2][bt2_grch38_1kgmaj_3], [.4.bt2][bt2_grch38_1kgmaj_4], [.rev.1.bt2][bt2_grch38_1kgmaj_r1], [.rev.2.bt2][bt2_grch38_1kgmaj_r2]
Human / GRCh37                            | [Ensembl][bt2_grch37_source] via [iGenomes]       | [full zip][bt2_grch37_full], [.1.bt2][bt2_grch37_1], [.2.bt2][bt2_grch37_2], [.3.bt2][bt2_grch37_3], [.4.bt2][bt2_grch37_4], [.rev.1.bt2][bt2_grch37_r1], [.rev.2.bt2][bt2_grch37_r2]
Human / Ash1.7 <sup>2</sup>               | [JHU][bt2_ash1_source]                            | [full zip][bt2_ash1_full], [.1.bt2][bt2_ash1_1], [.2.bt2][bt2_ash1_2], [.3.bt2][bt2_ash1_3], [.4.bt2][bt2_ash1_4], [.rev.1.bt2][bt2_ash1_r1], [.rev.2.bt2][bt2_ash1_r2]
Human / hg19                              | [UCSC][bt2_hg19_source]                           | [full zip][bt2_hg19_full], [.1.bt2][bt2_hg19_1], [.2.bt2][bt2_hg19_2], [.3.bt2][bt2_hg19_3], [.4.bt2][bt2_hg19_4], [.rev.1.bt2][bt2_hg19_r1], [.rev.2.bt2][bt2_hg19_r2]
Human / hg18                              | [UCSC][bt2_hg18_source]                           | [full zip][bt2_hg18_full], [.1.bt2][bt2_hg18_1], [.2.bt2][bt2_hg18_2], [.3.bt2][bt2_hg18_3], [.4.bt2][bt2_hg18_4], [.rev.1.bt2][bt2_hg18_r1], [.rev.2.bt2][bt2_hg18_r2]
Mouse / GRCm38                            | [NCBI][bt2_grcm38_source] via [iGenomes]          | [full zip][bt2_grcm38_full], [.1.bt2][bt2_grcm38_1], [.2.bt2][bt2_grcm38_2], [.3.bt2][bt2_grcm38_3], [.4.bt2][bt2_grcm38_4], [.rev.1.bt2][bt2_grcm38_r1], [.rev.2.bt2][bt2_grcm38_r2]
Mouse / mm10                              | [UCSC][bt2_mm10_source]                           | [full zip][bt2_mm10_full], [.1.bt2][bt2_mm10_1], [.2.bt2][bt2_mm10_2], [.3.bt2][bt2_mm10_3], [.4.bt2][bt2_mm10_4], [.rev.1.bt2][bt2_mm10_r1], [.rev.2.bt2][bt2_mm10_r2]
Mouse / mm9                               | [UCSC][bt2_mm9_source]                            | [full zip][bt2_mm9_full], [.1.bt2][bt2_mm9_1], [.2.bt2][bt2_mm9_2], [.3.bt2][bt2_mm9_3], [.4.bt2][bt2_mm9_4], [.rev.1.bt2][bt2_mm9_r1], [.rev.2.bt2][bt2_mm9_r2]
Chimpanzee / CHIMP2.1.4                   | [Ensembl][bt2_chimp214_source] via [iGenomes]     | [full zip][bt2_chimp214_full], [.1.bt2][bt2_chimp214_1], [.2.bt2][bt2_chimp214_2], [.3.bt2][bt2_chimp214_3], [.4.bt2][bt2_chimp214_4], [.rev.1.bt2][bt2_chimp214_r1], [.rev.2.bt2][bt2_chimp214_r2]
Dog / CanFam3.1                           | [Ensembl][bt2_canfam31_source] via [iGenomes]     | [full zip][bt2_canfam31_full], [.1.bt2][bt2_canfam31_1], [.2.bt2][bt2_canfam31_2], [.3.bt2][bt2_canfam31_3], [.4.bt2][bt2_canfam31_4], [.rev.1.bt2][bt2_canfam31_r1], [.rev.2.bt2][bt2_canfam31_r2]
Rat / rn4                                 | [UCSC][bt2_rn4_source]                            | [full zip][bt2_rn4_full], [.1.bt2][bt2_rn4_1], [.2.bt2][bt2_rn4_2], [.3.bt2][bt2_rn4_3], [.4.bt2][bt2_rn4_4], [.rev.1.bt2][bt2_rn4_r1], [.rev.2.bt2][bt2_rn4_r2]
Rat / Rnor6.0                             | [NCBI][bt2_rnor60_source] via [iGenomes]          | [full zip][bt2_rnor60_full], [.1.bt2][bt2_rnor60_1], [.2.bt2][bt2_rnor60_2], [.3.bt2][bt2_rnor60_3], [.4.bt2][bt2_rnor60_4], [.rev.1.bt2][bt2_rnor60_r1], [.rev.2.bt2][bt2_rnor60_r2]
Chicken / Galgal4                         | [Ensembl][bt2_galgal4_source] via [iGenomes]      | [full zip][bt2_galgal4_full], [.1.bt2][bt2_galgal4_1], [.2.bt2][bt2_galgal4_2], [.3.bt2][bt2_galgal4_3], [.4.bt2][bt2_galgal4_4], [.rev.1.bt2][bt2_galgal4_r1], [.rev.2.bt2][bt2_galgal4_r2]
Corn / AGPv4                              | [Ensembl][bt2_agpv4_source] via [iGenomes]        | [full zip][bt2_agpv4_full], [.1.bt2][bt2_agpv4_1], [.2.bt2][bt2_agpv4_2], [.3.bt2][bt2_agpv4_3], [.4.bt2][bt2_agpv4_4], [.rev.1.bt2][bt2_agpv4_r1], [.rev.2.bt2][bt2_agpv4_r2]
Zebrafish / GRCz10                        | [NCBI][bt2_grcz10_source] via [iGenomes]          | [full zip][bt2_grcz10_full], [.1.bt2][bt2_grcz10_1], [.2.bt2][bt2_grcz10_2], [.3.bt2][bt2_grcz10_3], [.4.bt2][bt2_grcz10_4], [.rev.1.bt2][bt2_grcz10_r1], [.rev.2.bt2][bt2_grcz10_r2]
Arabidopsis thaliana / TAIR10             | [Ensembl][bt2_tair10_source] via [iGenomes]        | [full zip][bt2_tair10_full], [.1.bt2][bt2_tair10_1], [.2.bt2][bt2_tair10_2], [.3.bt2][bt2_tair10_3], [.4.bt2][bt2_tair10_4], [.rev.1.bt2][bt2_tair10_r1], [.rev.2.bt2][bt2_tair10_r2]
Fruitfly / BDGP6                          | [Ensembl][bt2_bdgp6_source] via [iGenomes]        | [full zip][bt2_bdgp6_full], [.1.bt2][bt2_bdgp6_1], [.2.bt2][bt2_bdgp6_2], [.3.bt2][bt2_bdgp6_3], [.4.bt2][bt2_bdgp6_4], [.rev.1.bt2][bt2_bdgp6_r1], [.rev.2.bt2][bt2_bdgp6_r2]
C. elegans / WBcel235                     | [Ensembl][bt2_wbcel235_source] via [iGenomes]     | [full zip][bt2_wbcel235_full], [.1.bt2][bt2_wbcel235_1], [.2.bt2][bt2_wbcel235_2], [.3.bt2][bt2_wbcel235_3], [.4.bt2][bt2_wbcel235_4], [.rev.1.bt2][bt2_wbcel235_r1], [.rev.2.bt2][bt2_wbcel235_r2]
Yeast / R64-1-1                           | [Ensembl][bt2_r6411_source] via [iGenomes]        | [full zip][bt2_r6411_full], [.1.bt2][bt2_r6411_1], [.2.bt2][bt2_r6411_2], [.3.bt2][bt2_r6411_3], [.4.bt2][bt2_r6411_4], [.rev.1.bt2][bt2_r6411_r1], [.rev.2.bt2][bt2_r6411_r2]

<div class="datatable-end"></div>

[1000 Genomes]: https://www.internationalgenome.org
[iGenomes]: https://support.illumina.com/sequencing/sequencing_software/igenome.html

1. Major SNVs determined from [1000 Genomes Project](https://www.internationalgenome.org) variant calls.  [Details here](https://github.com/BenLangmead/bowtie-majref).
2. Ashkenazi reference genome from [10.1186/s13059-020-02047-7](https://doi.org/10.1186/s13059-020-02047-7)

[bt2_GRCh38_source]: ftp://ftp.ncbi.nlm.nih.gov/genomes/archive/old_genbank/Eukaryotes/vertebrates_mammals/Homo_sapiens/GRCh38/seqs_for_alignment_pipelines/
[bt2_GRCh38_full]: https://aws.amazon.com
[bt2_GRCh38_1]: https://aws.amazon.com
[bt2_GRCh38_2]: https://aws.amazon.com
[bt2_GRCh38_3]: https://aws.amazon.com
[bt2_GRCh38_4]: https://aws.amazon.com
[bt2_GRCh38_r1]: https://aws.amazon.com
[bt2_GRCh38_r2]: https://aws.amazon.com

[bt2_grch38_1kgmaj_source]: ftp://ftp.ccb.jhu.edu/pub/data/bowtie2_indexes/
[bt2_grch38_1kgmaj_full]: https://aws.amazon.com
[bt2_grch38_1kgmaj_1]: https://aws.amazon.com
[bt2_grch38_1kgmaj_2]: https://aws.amazon.com
[bt2_grch38_1kgmaj_3]: https://aws.amazon.com
[bt2_grch38_1kgmaj_4]: https://aws.amazon.com
[bt2_grch38_1kgmaj_r1]: https://aws.amazon.com
[bt2_grch38_1kgmaj_r2]: https://aws.amazon.com

[bt2_grch37_source]: https://grch37.ensembl.org/index.html
[bt2_grch37_full]: https://aws.amazon.com
[bt2_grch37_1]: https://aws.amazon.com
[bt2_grch37_2]: https://aws.amazon.com
[bt2_grch37_3]: https://aws.amazon.com
[bt2_grch37_4]: https://aws.amazon.com
[bt2_grch37_r1]: https://aws.amazon.com
[bt2_grch37_r2]: https://aws.amazon.com

[bt2_ash1_source]: ftp://ftp.ccb.jhu.edu/pub/data/Homo_sapiens/Ash1/v1.7/Assembly/
[bt2_ash1_full]: https://aws.amazon.com
[bt2_ash1_1]: https://aws.amazon.com
[bt2_ash1_2]: https://aws.amazon.com
[bt2_ash1_3]: https://aws.amazon.com
[bt2_ash1_4]: https://aws.amazon.com
[bt2_ash1_r1]: https://aws.amazon.com
[bt2_ash1_r2]: https://aws.amazon.com

[bt2_hg19_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/chromosomes
[bt2_hg19_full]: https://aws.amazon.com
[bt2_hg19_1]: https://aws.amazon.com
[bt2_hg19_2]: https://aws.amazon.com
[bt2_hg19_3]: https://aws.amazon.com
[bt2_hg19_4]: https://aws.amazon.com
[bt2_hg19_r1]: https://aws.amazon.com
[bt2_hg19_r2]: https://aws.amazon.com

[bt2_hg18_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/hg18/chromosomes
[bt2_hg18_full]: https://aws.amazon.com
[bt2_hg18_1]: https://aws.amazon.com
[bt2_hg18_2]: https://aws.amazon.com
[bt2_hg18_3]: https://aws.amazon.com
[bt2_hg18_4]: https://aws.amazon.com
[bt2_hg18_r1]: https://aws.amazon.com
[bt2_hg18_r2]: https://aws.amazon.com

[bt2_chimp214_source]: https://useast.ensembl.org/Pan_troglodytes/Info/Index
[bt2_chimp214_full]: https://aws.amazon.com
[bt2_chimp214_1]: https://aws.amazon.com
[bt2_chimp214_2]: https://aws.amazon.com
[bt2_chimp214_3]: https://aws.amazon.com
[bt2_chimp214_4]: https://aws.amazon.com
[bt2_chimp214_r1]: https://aws.amazon.com
[bt2_chimp214_r2]: https://aws.amazon.com

[bt2_canfam31_source]: https://www.ensembl.org/Canis_lupus_familiaris/Info/Index
[bt2_canfam31_full]: https://aws.amazon.com
[bt2_canfam31_1]: https://aws.amazon.com
[bt2_canfam31_2]: https://aws.amazon.com
[bt2_canfam31_3]: https://aws.amazon.com
[bt2_canfam31_4]: https://aws.amazon.com
[bt2_canfam31_r1]: https://aws.amazon.com
[bt2_canfam31_r2]: https://aws.amazon.com

[bt2_grcm38_source]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001635.20/
[bt2_grcm38_full]: https://aws.amazon.com
[bt2_grcm38_1]: https://aws.amazon.com
[bt2_grcm38_2]: https://aws.amazon.com
[bt2_grcm38_3]: https://aws.amazon.com
[bt2_grcm38_4]: https://aws.amazon.com
[bt2_grcm38_r1]: https://aws.amazon.com
[bt2_grcm38_r2]: https://aws.amazon.com

[bt2_mm10_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/mm10/chromosomes
[bt2_mm10_full]: https://aws.amazon.com
[bt2_mm10_1]: https://aws.amazon.com
[bt2_mm10_2]: https://aws.amazon.com
[bt2_mm10_3]: https://aws.amazon.com
[bt2_mm10_4]: https://aws.amazon.com
[bt2_mm10_r1]: https://aws.amazon.com
[bt2_mm10_r2]: https://aws.amazon.com

[bt2_mm9_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/mm9/chromosomes
[bt2_mm9_full]: https://aws.amazon.com
[bt2_mm9_1]: https://aws.amazon.com
[bt2_mm9_2]: https://aws.amazon.com
[bt2_mm9_3]: https://aws.amazon.com
[bt2_mm9_4]: https://aws.amazon.com
[bt2_mm9_r1]: https://aws.amazon.com
[bt2_mm9_r2]: https://aws.amazon.com

[bt2_rn4_source]: ftp://hgdownload.cse.ucsc.edu/goldenPath/rn4/chromosomes
[bt2_rn4_full]: https://aws.amazon.com
[bt2_rn4_1]: https://aws.amazon.com
[bt2_rn4_2]: https://aws.amazon.com
[bt2_rn4_3]: https://aws.amazon.com
[bt2_rn4_4]: https://aws.amazon.com
[bt2_rn4_r1]: https://aws.amazon.com
[bt2_rn4_r2]: https://aws.amazon.com

[bt2_rnor60_source]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000001895.5/
[bt2_rnor60_full]: https://aws.amazon.com
[bt2_rnor60_1]: https://aws.amazon.com
[bt2_rnor60_2]: https://aws.amazon.com
[bt2_rnor60_3]: https://aws.amazon.com
[bt2_rnor60_4]: https://aws.amazon.com
[bt2_rnor60_r1]: https://aws.amazon.com
[bt2_rnor60_r2]: https://aws.amazon.com

[bt2_galgal4_source]: http://jul2016.archive.ensembl.org/Gallus_gallus/Info/Index
[bt2_galgal4_full]: https://aws.amazon.com
[bt2_galgal4_1]: https://aws.amazon.com
[bt2_galgal4_2]: https://aws.amazon.com
[bt2_galgal4_3]: https://aws.amazon.com
[bt2_galgal4_4]: https://aws.amazon.com
[bt2_galgal4_r1]: https://aws.amazon.com
[bt2_galgal4_r2]: https://aws.amazon.com

[bt2_agpv4_source]: http://plants.ensembl.org/Zea_mays/Info/Index
[bt2_agpv4_full]: https://aws.amazon.com
[bt2_agpv4_1]: https://aws.amazon.com
[bt2_agpv4_2]: https://aws.amazon.com
[bt2_agpv4_3]: https://aws.amazon.com
[bt2_agpv4_4]: https://aws.amazon.com
[bt2_agpv4_r1]: https://aws.amazon.com
[bt2_agpv4_r2]: https://aws.amazon.com

[bt2_grcz10_source]: https://useast.ensembl.org/Drosophila_melanogaster/Info/Index
[bt2_grcz10_full]: https://aws.amazon.com
[bt2_grcz10_1]: https://aws.amazon.com
[bt2_grcz10_2]: https://aws.amazon.com
[bt2_grcz10_3]: https://aws.amazon.com
[bt2_grcz10_4]: https://aws.amazon.com
[bt2_grcz10_r1]: https://aws.amazon.com
[bt2_grcz10_r2]: https://aws.amazon.com

[bt2_tair10_source]: http://plants.ensembl.org/Arabidopsis_thaliana/Info/Index
[bt2_tair10_full]: https://aws.amazon.com
[bt2_tair10_1]: https://aws.amazon.com
[bt2_tair10_2]: https://aws.amazon.com
[bt2_tair10_3]: https://aws.amazon.com
[bt2_tair10_4]: https://aws.amazon.com
[bt2_tair10_r1]: https://aws.amazon.com
[bt2_tair10_r2]: https://aws.amazon.com

[bt2_bdgp6_source]: https://www.ncbi.nlm.nih.gov/assembly/GCF_000002035.5/
[bt2_bdgp6_full]: https://aws.amazon.com
[bt2_bdgp6_1]: https://aws.amazon.com
[bt2_bdgp6_2]: https://aws.amazon.com
[bt2_bdgp6_3]: https://aws.amazon.com
[bt2_bdgp6_4]: https://aws.amazon.com
[bt2_bdgp6_r1]: https://aws.amazon.com
[bt2_bdgp6_r2]: https://aws.amazon.com

[bt2_wbcel235_source]: https://www.ensembl.org/Caenorhabditis_elegans/Info/Index
[bt2_wbcel235_full]: https://aws.amazon.com
[bt2_wbcel235_1]: https://aws.amazon.com
[bt2_wbcel235_2]: https://aws.amazon.com
[bt2_wbcel235_3]: https://aws.amazon.com
[bt2_wbcel235_4]: https://aws.amazon.com
[bt2_wbcel235_r1]: https://aws.amazon.com
[bt2_wbcel235_r2]: https://aws.amazon.com

[bt2_r6411_source]: https://www.ensembl.org/Saccharomyces_cerevisiae/Info/Index
[bt2_r6411_full]: https://aws.amazon.com
[bt2_r6411_1]: https://aws.amazon.com
[bt2_r6411_2]: https://aws.amazon.com
[bt2_r6411_3]: https://aws.amazon.com
[bt2_r6411_4]: https://aws.amazon.com
[bt2_r6411_r1]: https://aws.amazon.com
[bt2_r6411_r2]: https://aws.amazon.com
