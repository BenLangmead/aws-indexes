Remember that if you need temporary credentials, you can go to:
https://jh.awsapps.com/start/#/console?account_id=159168350739

Unfortunately, my instance_shopper.py script doesn't know about architectures (e.g. Xeon versus Graviton).  Another factor that's important is whether there's instance-local storage.  So it could be that I have to narrow my options using more than one script or database.

I guess you look at the instance "series" info for this:

a – AMD processors
b*00 | gb*00 – Accelerated by NVIDIA Blackwell GPUs
g – AWS Graviton processors
i – Intel processors
m* | m*pro– Apple chip
b – Block storage optimization
d – Instance store volumes
e – Extra instance storage (for storage optimized instance types), extra memory (for memory optimized instance types), or extra GPU memory (for accelerated computing instance types).
flex – Flex instance

Given this, I think these are relevant instances:

r8gd.metal-48xl, Graviton, 1.5TB
ca-central-1, eu-central-1, sa-east-1, $2.40--$2.70

x2idn.24xlarge, Intel, 1.5TB
eu-west-2, eu-west-3, eu-north-1, eu-central-1, ca-central-1, ap-northeast-3, $1.30--$1.45

x2idn.16xlarge, Intel, 1TB
us-east-2, eu-north-1, $0.90--$1.20

x2iedn.metal,Intel, 4 TB
us-east-2,eu-north-1, $2.70--$3.05