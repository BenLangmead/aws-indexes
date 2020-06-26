Public hosting of these index files is possible thanks to the Amazon Web Services [Public Dataset Program](https://aws.amazon.com/opendata/public-datasets/).
Use the left sidebar to select a tool.

Each index file can be accessed freely and without charge through either an HTTPS URL or an S3 URL.

To access files from *within AWS*, e.g. from an EC2 instance, you can use the [AWS CLI](https://aws.amazon.com/cli/) to perform an S3 `copy` or `sync`, using a command like this:

```buildoutcfg
aws s3 cp s3://genome-idx/bt/grch38_1kgmaj.zip .
```

You can also initiate transfers using the [AWS console](https://aws.amazon.com/console/), the Python [`boto3` library](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), and various other tools and libraries.

Access to files in the [AWS Public Dataset Program](https://aws.amazon.com/opendata/public-datasets/) is *free*.  This is true whether you use the HTTPS or the S3 URL.  For S3 URLs, the transfer is free even if it crosses an AWS region boundary; there is no [inter-regional data transfer fee](https://aws.amazon.com/s3/pricing/).

To get started with these index files, please see the tutorials for the respective tools.

* [Bowtie tutorial](http://bowtie-bio.sourceforge.net/tutorial.shtml)
* [Bowtie 2 tutorial](http://bowtie-bio.sourceforge.net/bowtie2/manual.shtml#getting-started-with-bowtie-2-lambda-phage-example)
* [HISAT2 HOWTO guide](https://daehwankimlab.github.io/hisat2/howto/)
* [HISAT-genotype tutorials](https://daehwankimlab.github.io/hisat-genotype/tutorials/)
* [Centrifuge getting started guide](https://ccb.jhu.edu/software/centrifuge/manual.shtml#getting-started-with-centrifuge)
* Kraken 2 manual
    * [Classifying reads](https://github.com/DerrickWood/kraken2/wiki/Manual#classification)
