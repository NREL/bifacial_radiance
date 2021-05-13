## Batch Launcher

This script requires the `boto3` Python AWS SDK to be installed, and the user to have valid AWS credentials available.

### Usage
```sh
$ python3 aws-batch.py -h

usage: aws-batch.py [-h] [--region REGION] [--subnet SUBNET] [--vpc VPC]
                    [--security-group SECURITY_GROUP] [--name NAME]
                    <ACTION>

positional arguments:
  <ACTION>              "create" or "delete"

optional arguments:
  -h, --help            show this help message and exit
  --region REGION       The AWS region to search (default is us-west-2)
  --subnet SUBNET       Subnet-id of the subnet that the AWS Batch
                        compute environment should use
  --vpc VPC             Vpc-id of the VPC that the AWS Batch compute
                        environment should use
  --security-group SECURITY_GROUP
                        Security-group-id of the security-group that the
                        AWS Batch compute environment should use
  --name NAME           Name to use as a namespace for all batch-related
                        resources in this deployment (defaults to
                        "bifacial-radiance")
```

Example:
`python3 aws-batch.py --vpc vpc-******** --subnet subnet-******** --security-group sg-************* --name batch-job-name create`

Clean up an existing batch configuration by running `python3 aws-batch.py --name batch-job-name delete`