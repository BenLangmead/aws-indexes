# Bowtie 2 indexes

[Bowtie](http://bowtie-bio.sourceforge.net) and [Bowtie 2](http://bowtie-bio.sourceforge.net/bowtie2) are read aligners for sequencing reads.  Bowtie specializes in short reads, generally about 50bp or shorter.  Bowtie 2 specializes in longer reads, up to around hundreds of base pairs.

In the past, Bowtie 1 & 2 had incompatible genome indexes.  This changed in July 2019 when Bowtie v1.2.3 gained the ability to use Bowtie 2 formatted genome indexes (ending in `.bt2`).  We list only Bowtie 2-format `.bt2` index files here.

See the manuals for Bowtie & Bowtie 2 for further details.

Note: all links are placeholders for now.  They will be replaced when the public repo is available.

<div class="datatable-begin"></div>

Species | Build      | FASTA source | Files       | Ref
------- | ---------  | ------------ | ----------- | -----
Human   | hg38       | [UCSC][bt2_hg38_source] | [full zip][bt2_hg38_full], [.1.bt2][bt2_hg38_1], [.2.bt2][bt2_hg38_2], [.3.bt2][bt2_hg38_3], [.4.bt2][bt2_hg38_4], [.rev.1.bt2][bt2_hg38_r1], [.rev.2.bt2][bt2_hg38_r2] | -
Human   | GRCh38     | [NCBI][bt2_GRCh38_source]     | [full zip][bt2_GRCh38_full], [.1.bt2][bt2_GRCh38_1], [.2.bt2][bt2_GRCh38_2], [.3.bt2][bt2_GRCh38_3], [.4.bt2][bt2_GRCh38_4], [.rev.1.bt2][bt2_GRCh38_r1], [.rev.2.bt2][bt2_GRCh38_r2] | [10.1101%2Fgr.213611.116](https://dx.doi.org/10.1101%2Fgr.213611.116)
Human   | GRCh38 + major SNVs* | [NCBI][bt2_grch38_1kgmaj_source] | [full zip][bt2_grch38_1kgmaj_full], [.1.bt2][bt2_grch38_1kgmaj_1], [.2.bt2][bt2_grch38_1kgmaj_2], [.3.bt2][bt2_grch38_1kgmaj_3], [.4.bt2][bt2_grch38_1kgmaj_4], [.rev.1.bt2][bt2_grch38_1kgmaj_r1], [.rev.2.bt2][bt2_grch38_1kgmaj_r2] | -
Human   | Ash1.7 | [JHU][bt2_ash1_source] | [full zip][bt2_ash1_full], [.1.bt2][bt2_ash1_1], [.2.bt2][bt2_ash1_2], [.3.bt2][bt2_ash1_3], [.4.bt2][bt2_ash1_4], [.rev.1.bt2][bt2_ash1_r1], [.rev.2.bt2][bt2_ash1_r2] | [10.1186/s13059-020-02047-7](https://doi.org/10.1186/s13059-020-02047-7)
Human   | hg19 | [UCSC][bt2_hg19_source] | [full zip][bt2_hg19_full], [.1.bt2][bt2_hg19_1], [.2.bt2][bt2_hg19_2], [.3.bt2][bt2_hg19_3], [.4.bt2][bt2_hg19_4], [.rev.1.bt2][bt2_hg19_r1], [.rev.2.bt2][bt2_hg19_r2] | -
Human   | hg18 | [UCSC][bt2_hg18_source] | [full zip][bt2_hg18_full], [.1.bt2][bt2_hg18_1], [.2.bt2][bt2_hg18_2], [.3.bt2][bt2_hg18_3], [.4.bt2][bt2_hg18_4], [.rev.1.bt2][bt2_hg18_r1], [.rev.2.bt2][bt2_hg18_r2] | -
Mouse   | mm10 | [UCSC][bt2_mm10_source] | [full zip][bt2_mm10_full], [.1.bt2][bt2_mm10_1], [.2.bt2][bt2_mm10_2], [.3.bt2][bt2_mm10_3], [.4.bt2][bt2_mm10_4], [.rev.1.bt2][bt2_mm10_r1], [.rev.2.bt2][bt2_mm10_r2] | -
Mouse   | mm9 | [UCSC][bt2_mm9_source] | [full zip][bt2_mm9_full], [.1.bt2][bt2_mm9_1], [.2.bt2][bt2_mm9_2], [.3.bt2][bt2_mm9_3], [.4.bt2][bt2_mm9_4], [.rev.1.bt2][bt2_mm9_r1], [.rev.2.bt2][bt2_mm9_r2] | -
Rat   | rn4 | [UCSC][bt2_rn4_source] | [full zip][bt2_rn4_full], [.1.bt2][bt2_rn4_1], [.2.bt2][bt2_rn4_2], [.3.bt2][bt2_rn4_3], [.4.bt2][bt2_rn4_4], [.rev.1.bt2][bt2_rn4_r1], [.rev.2.bt2][bt2_rn4_r2] | -

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

[bt2_ash1_source]: https://aws.amazon.com
[bt2_ash1_full]: https://aws.amazon.com
[bt2_ash1_1]: https://aws.amazon.com
[bt2_ash1_2]: https://aws.amazon.com
[bt2_ash1_3]: https://aws.amazon.com
[bt2_ash1_4]: https://aws.amazon.com
[bt2_ash1_r1]: https://aws.amazon.com
[bt2_ash1_r2]: https://aws.amazon.com

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
