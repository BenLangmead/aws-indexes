# SPUMONI indexes

SPUMONI is a fast read classification tool for targeted nanopore sequencing.  It uses a compressed r-index together with a streaming matching-statistics algorithm and statsitical test to classify reads. 

The exact accession ids used for the reference genomes in the Zymo mock community indexes can be [found here][accessions] ([s3 link][accessions_s3]).

<div class="datatable-begin"></div>

Collection                                              | Date            | HTTPS URL                                                                         | S3 URL
------------------------------------------------------- | --------------- | --------------------------------------------------------------------------------- | -----------------------------------------------------------------------------------------
Zymo mock community, one genome, matching strain        |  March, 2021    | [positive.spumoni][zymo_pos_one_match], [null.spumoni][zymo_null_one_match]       | [positive.spumoni][zymo_pos_one_match_s3], [null.spumoni][zymo_null_one_match_s3]
Zymo mock community, one genome, non-matching strain    |  March, 2021    | [positive.spumoni][zymo_pos_one_nonmatch], [null.spumoni][zymo_null_one_nonmatch] | [positive.spumoni][zymo_pos_one_nonmatch_s3], [null.spumoni][zymo_null_one_nonmatch_s3]
Zymo mock community, pan-genome, with matching strain   |  March, 2021    | [positive.spumoni][zymo_pos_all_match], [null.spumoni][zymo_null_all_match]       | [positive.spumoni][zymo_pos_all_match_s3], [null.spumoni][zymo_null_all_match_s3]
Zymo mock community, pan-genome, without matcing strain |  March, 2021    | [positive.spumoni][zymo_pos_all_nonmatch], [null.spumoni][zymo_null_all_nonmatch] | [positive.spumoni][zymo_pos_all_nonmatch_s3], [null.spumoni][zymo_null_all_nonmatch_s3]
Human, one genome (T2T CHM13 v1.0)                      |  March, 2021    | [positive.spumoni][human1_pos], [null.spumoni][human1_null]                       | [positive.spumoni][human1_pos_s3], [null.spumoni][human1_null_s3]
Human, three genomes (T2T CHM13 v1.0, Ashv2.0, GRCh38)  |  March, 2021    | [positive.spumoni][human3_pos], [null.spumoni][human3_null]                       | [positive.spumoni][human3_pos_s3], [null.spumoni][human3_null_s3]

<div class="datatable-end"></div>

SPUMONI is the work of Omar Ahmed, Massimiliano Rossi, Sam Kovaka, Michael C. Schatz, Travis Gagie, Christina Boucher, and Ben Langmead.

[accessions]: https://genome-idx.s3.amazonaws.com/spumoni/refseq_accession_nums/accessions.zip
[accessions_s3]: s3://genome-idx/spumoni/refseq_accession_nums/accessions.zip

[zymo_pos_one_match]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_one_genome_with_zymo_refs/mock_comm_one_genome_with_zymo_refs_positive_index.spumoni
[zymo_null_one_match]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_one_genome_with_zymo_refs/mock_comm_one_genome_with_zymo_refs_null_index.spumoni
[zymo_pos_one_nonmatch]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_one_genome_without_zymo_refs/mock_comm_one_genome_without_zymo_refs_positive_index.spumoni
[zymo_null_one_nonmatch]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_one_genome_without_zymo_refs/mock_comm_one_genome_without_zymo_refs_null_index.spumoni

[zymo_pos_one_match_s3]: s3://genome-idx/spumoni/mock_comm_one_genome_with_zymo_refs/mock_comm_one_genome_with_zymo_refs_positive_index.spumoni
[zymo_null_one_match_s3]: s3://genome-idx/spumoni/mock_comm_one_genome_with_zymo_refs/mock_comm_one_genome_with_zymo_refs_null_index.spumoni
[zymo_pos_one_nonmatch_s3]: s3://genome-idx/spumoni/mock_comm_one_genome_without_zymo_refs/mock_comm_one_genome_without_zymo_refs_positive_index.spumoni
[zymo_null_one_nonmatch_s3]: s3://genome-idx/spumoni/mock_comm_one_genome_without_zymo_refs/mock_comm_one_genome_without_zymo_refs_null_index.spumoni

[zymo_pos_all_match]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_all_genomes_with_zymo_refs/mock_comm_all_genomes_with_zymo_refs_positive_index.spumoni
[zymo_null_all_match]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_all_genomes_with_zymo_refs/mock_comm_all_genomes_with_zymo_refs_null_index.spumoni
[zymo_pos_all_nonmatch]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_all_genomes_without_zymo_refs/mock_comm_all_genomes_without_zymo_refs_positive_index.spumoni
[zymo_null_all_nonmatch]: https://genome-idx.s3.amazonaws.com/spumoni/mock_comm_all_genomes_without_zymo_refs/mock_comm_all_genomes_without_zymo_refs_null_index.spumoni

[zymo_pos_all_match_s3]: s3://genome-idx/spumoni/mock_comm_all_genomes_with_zymo_refs/mock_comm_all_genomes_with_zymo_refs_positive_index.spumoni
[zymo_null_all_match_s3]: s3://genome-idx/spumoni/mock_comm_all_genomes_with_zymo_refs/mock_comm_all_genomes_with_zymo_refs_null_index.spumoni
[zymo_pos_all_nonmatch_s3]: s3://genome-idx/spumoni/mock_comm_all_genomes_without_zymo_refs/mock_comm_all_genomes_without_zymo_refs_positive_index.spumoni
[zymo_null_all_nonmatch_s3]: s3://genome-idx/spumoni/mock_comm_all_genomes_without_zymo_refs/mock_comm_all_genomes_without_zymo_refs_null_index.spumoni

[human1_pos]: https://genome-idx.s3.amazonaws.com/spumoni/one_human_genome/one_human_genome_positive_index.spumoni
[human1_null]: https://genome-idx.s3.amazonaws.com/spumoni/one_human_genome/one_human_genome_null_index.spumoni
[human1_pos_s3]: s3://genome-idx/spumoni/one_human_genome/one_human_genome_positive_index.spumoni
[human1_null_s3]: s3://genome-idx/spumoni/one_human_genome/one_human_genome_null_index.spumoni

[human3_pos]: https://genome-idx.s3.amazonaws.com/spumoni/three_human_genomes/three_human_genomes_positive_index.spumoni
[human3_null]: https://genome-idx.s3.amazonaws.com/spumoni/three_human_genomes/three_human_genomes_null_index.spumoni
[human3_pos_s3]: s3://genome-idx/spumoni/three_human_genomes/three_human_genomes_positive_index.spumoni
[human3_null_s3]: s3://genome-idx/spumoni/three_human_genomes/three_human_genomes_null_index.spumoni
