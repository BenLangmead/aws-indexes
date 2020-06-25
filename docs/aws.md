To access these files from within AWS, e.g. from an EC2 instance, you can use the [AWS CLI](https://aws.amazon.com/cli/) to perform an S3 `copy` or `sync`, using a command like this:

```buildoutcfg
aws s3 cp s3://genome-idx/bt/grch38_1kgmaj.zip .
```

You can also initiate transfers using the [AWS console](https://aws.amazon.com/console/), the Python [`boto3` library](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html), and various other tools and libraries.

Note that access to files in the [AWS Public Dataset Program](https://aws.amazon.com/opendata/public-datasets/) is :moneybag: free :moneybag:, even if the transfer is across AWS regions.  You do not need to pay [an inter-regional data transfer fee](https://aws.amazon.com/s3/pricing/).
