If you would like to access files in the data regsitry from within AWS, e.g. from an EC2 instance, then you can use the [AWS CLI](https://aws.amazon.com/cli/) to perform the transfer, using a command like this:

```buildoutcfg
aws s3 cp s3://.../xyz .
```

If you are issuing this command from an EC2 instance, note that the instance must be able to find and use your EC2 credentials.

Note that access to files in the [AWS Public Dataset Program](https://aws.amazon.com/opendata/public-datasets/) is :moneybag: free :moneybag:, even if you are transfering the data across regions within AWS.  You need not pay the typical [inter-regional data transfer cost](https://aws.amazon.com/s3/pricing/).
