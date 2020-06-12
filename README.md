# aws-indexes

Catalog of genomic indexes freely available from public clouds.  Meant to be viewed as a [GitHub Pages website](https://benlangmead.github.io/aws-indexes/).

We expect this resource will be useful to regular users of Bowtie (1 & 2), HISAT2, Kraken 2/Bracken and Centrifuge.  The links will allow downloads from `https://` URLs, so users can download from anywhere.

Users working in the cloud, e.g. on AWS EC2 instances, gain a particular advantage because they can potentially download the data directly (e.g. using the AWS CLI) from the same AWS region where their instance is located.  That is the best case scenario both for speed of download and for cost (free!).  Another good scenario, slightly worse than the previous, is if the user is working in an AWS region other than the one where our indexes are stored.  In that case, speed will be someone worse and it will cost something (since data must move between AWS regions).

# Other resources

Many thanks to Illunina for maintaining the excellent [iGenomes](https://support.illumina.com/sequencing/sequencing_software/igenome.html) resource.

For access to [iGenomes](https://support.illumina.com/sequencing/sequencing_software/igenome.html)-style indexes, sequences and annotations, check out [AWS iGenomes](https://ewels.github.io/AWS-iGenomes/).  These are best accessed from AWS (e.g. from EC2 instances) in region `eu-west-1`.
