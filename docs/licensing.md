---
title: Data licensing
---

# Data licensing

## Our contribution

We place no restrictions of our own on the index files hosted in the `genome-idx` bucket. You may use them, and results produced with them, for any purpose, including commercial purposes.

The MIT license at the top of the [GitHub repository](https://github.com/BenLangmead/aws-indexes) covers the code and documentation in that repository. It does not describe the terms of the data the indexes are built from.

## Terms of the underlying data

Each index is built from sequences, and often a taxonomy, published by a third party. Those inputs keep their original terms, and the terms of an index follow from them. The per-index pages name the sources, and many indexes ship a `library_report.tsv` file listing the origin of every sequence.

Source | Used by | Terms
------ | ------- | -----
[NCBI](https://www.ncbi.nlm.nih.gov/) (RefSeq, GenBank, UniVec, NCBI Taxonomy) | Kraken 2 Refseq collections (Viral, MinusB, Standard, PlusPF, PlusPFP and their capped versions), core_nt, and most other indexes | NCBI places no restrictions on the use or distribution of its data, but notes that some submitters may claim patent, copyright or other intellectual property rights in the sequences they submitted. See [NCBI's policies and disclaimers](https://www.ncbi.nlm.nih.gov/home/about/policies/).
[GTDB](https://gtdb.ecogenomic.org/) | Kraken 2 GTDB indexes | [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see [GTDB licenses](https://gtdb.ecogenomic.org/licenses)). Commercial use is allowed. Because these indexes are derived from GTDB genomes and taxonomy, we distribute them under CC BY-SA 4.0 as well: credit GTDB, and redistribute adapted versions under the same license.
[SILVA](https://www.arb-silva.de/) | Indexes built from SILVA releases | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) (see [SILVA license information](https://www.arb-silva.de/silva-license-information/)). Commercial use is allowed with credit to SILVA. SILVA notes that commercial users may have benefit-sharing obligations under the Convention on Biological Diversity.

For indexes built from other sources, such as EuPathDB or human pangenome assemblies, consult the terms published by that source.

This page summarizes the terms as we understand them and is not legal advice. If you need a definitive statement for a license register, check the source terms directly.

Questions can go to the [issue tracker](https://github.com/BenLangmead/aws-indexes/issues).
