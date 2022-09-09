# SPUMONI 2 indexes

SPUMONI 2 ([GitHub repo](https://github.com/oma219/spumoni)) is a fast read classification tool that improves on the SPUMONI algorithm by integrating minimizer digestion, a sampled document array for multi-class classification, and improved support for both short and long reads. 

<div class="datatable-begin"></div>

Corresponding S3 URLs can be obtained by removing `https://genome-idx.s3.amazonaws.com` from the beginning of the URLs linked to above and replacing with `s3://genome-idx`.

Collection                                              | Date            | HTTPS URL                                                         |
------------------------------------------------------- |-----------------|-------------------------------------------------------------------|
Assembly contaminant pan-genome, SPUMONI 2 index        | September, 2022 | [tar.gz][assembly_contamination_index.tar.gz]
E. coli 500 pan-genome, FASTAs                          | September, 2022 | [tar.gz][ecoli_500_dataset.tar.gz]
Human assembly pan-genome, SPUMONI 2 index              | September, 2022 | [tar.gz][human_pangenome_ont_index.tar.gz]
Zymo mock community pan-genome, SPUMONI 2 index         | September, 2022 | [tar.gz][mock_community_ont_index.tar.gz]
8-species SPUMONI 2 index, including sampled doc array  | September, 2022 | [tar.gz][sampled_doc_array_index.tar.gz]

<div class="datatable-end"></div>

SPUMONI 2 is the work of Omar Ahmed, Massimiliano Rossi, Travis Gagie, Christina Boucher, and Ben Langmead.

[assembly_contamination_index.tar.gz]: https://genome-idx.s3.amazonaws.com/spu2/assembly_contamination_index.tar.gz
[ecoli_500_dataset.tar.gz]: https://genome-idx.s3.amazonaws.com/spu2/ecoli_500_dataset.tar.gz
[human_pangenome_ont_index.tar.gz]: https://genome-idx.s3.amazonaws.com/spu2/human_pangenome_ont_index.tar.gz
[mock_community_ont_index.tar.gz]: https://genome-idx.s3.amazonaws.com/spu2/mock_community_ont_index.tar.gz
[sampled_doc_array_index.tar.gz]: https://genome-idx.s3.amazonaws.com/spu2/sampled_doc_array_index.tar.gz