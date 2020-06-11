If you would like to access files in the data regsitry from within AWS, e.g. from an EC2 instance, then you can use the [AWS CLI](https://aws.amazon.com/cli/) to perform the transfer, using a command like this:

```buildoutcfg
aws s3 cp s3://.../xyz .
```

If you are issuing this command from an EC2 instance, note that the instance must be able to find and use your EC2 credentials.

Also note that all S3 files reside in a particular AWS region.  Our files reside in the region us-east-2 (Ohio).  If you access the files from a region other than that one, you will have to pay an inter-regional data transfer cost, [as detailed in the S3 documentation](https://aws.amazon.com/s3/pricing/).