#!/usr/bin/env python3
import boto3
import argparse
import sys
from botocore.errorfactory import ClientError
from time import sleep

"""
This script assumes the calling user has properly configured AWS credentials in
their home directory or in this process's environment.
    
For example, export an API keypair to the environment before running this script:
    $ export AWS_ACCESS_KEY_ID=****************
    $ export AWS_SECRET_ACCESS_KEY=****************
"""

executable_name = __file__.rpartition('/')[2]


def get_default_subnet_id(vpc_id):
    """return default subnet for a given VPC"""
    return (
        ec2
        .describe_subnets(
            Filters = [ { "Name": "vpc-id", "Values": [vpc_id] } ]
        )
        ["Subnets"]
        [0]
        ["SubnetId"]
    )
        
        
def get_default_vpc_id():
    """return ID of current account' kt2s default VPC"""
    try:
        return (
            ec2
            .describe_vpcs(
                Filters = [ { "Name": "isDefault", "Values": [ "true" ] } ]
            )
            ["Vpcs"]
            [0]
            ["VpcId"]
        )
        
    except IndexError:
        print("ERROR: The account associated with the current AWS account does not have a default VPC")
        print("Please specify a vpc-id with the '--vpc' flag")
        exit(1)


def get_default_security_group_id():
    """return ID of current account's default security group"""
    return (
        ec2
        .describe_security_groups(
            GroupNames = ["default"]
        )
        ["SecurityGroups"]
        [0]
        ["GroupId"]
    )
    
    
def get_compute_environment_status():
    global compute_environment_name
    return (
        batch
        .describe_compute_environments(
            computeEnvironments = [ compute_environment_name ]
        )
        ['computeEnvironments']
        [0]
        ['state']
    )


def wait_for_compute_environment_status(desired_status):
    global compute_environment_name
    
    print(
            f"Waiting for compute environment '{compute_environment_name}' to change to {desired_status}",
            end=''
        )
    
    for attempt in range(30):
        status = get_compute_environment_status()
        if status == desired_status:
            print("\nDONE")
            break
        
        print('.', end='')
        sys.stdout.flush()
        sleep(2)
        
    else:
        print(
            f"ERROR: Waiting for state-change of compute environment '{compute_environment_name}' to {desired_status} timed out.",
            file=sys.stderr
        )
        exit(1)


def update_compute_environment_status(desired_status):
    global compute_environment_name
    batch.update_compute_environment(
        computeEnvironment = compute_environment_name,
        state = desired_status
    )


###################################################################################



parser = argparse.ArgumentParser()

parser.add_argument(
    'action',
    metavar='<ACTION>',
    type=str,
    nargs=1,
    choices=['create', 'delete'],
    help='"create" or "delete"'
)
                    
parser.add_argument(
    "--region",
    type=str,
    help="The AWS region to search (default is us-west-2)",
    default='us-west-2'
)

parser.add_argument(
    "--subnet",
    type=str,
    help="Subnet-id of the subnet that the AWS Batch compute environment should use",
    default=None # need a VPC ID to run get_default_subnet_id()
)

parser.add_argument(
    "--vpc",
    type=str,
    help="Vpc-id of the VPC that the AWS Batch compute environment should use",
    default=None
)

parser.add_argument(
    "--security-group",
    type=str,
    help="Security-group-id of the security-group that the AWS Batch compute environment should use",
    default=None
)

parser.add_argument(
    "--name",
    type=str,
    help="Name to use as a namespace for all batch-related resources in this deployment (defaults to \"bifacial-radiance\")",
    default="bifacial-radiance"
)


args = parser.parse_args()


aws_session = boto3.Session()

for client_name in ["batch", "sts", "ec2", "iam"]:
    locals()[client_name] = aws_session.client(client_name, args.region)

account_id = sts.get_caller_identity()['Account']

args.action = args.action[0]

if not args.vpc:
    args.vpc = get_default_vpc_id()
    print(f"vpc-id not given, using account default '{args.vpc}'\n")
    
if not args.subnet:
    args.subnet = get_default_subnet_id(args.vpc)
    print(f"subnet-id not given, using account default '{args.subnet}'\n")
    
if not args.security_group:
    args.security_group = get_default_security_group_id()
    print(f"security-group-id not given, using account default '{args.security_group}'\n")
    

compute_environment_name = f"{args.name}-compute-environment"
job_queue_name = f"{args.name}-job-queue"
job_definition_name = f"{args.name}-job-definition"
batch_execution_role_name = f"{args.name}-execution-role"


compute_environment_description = (
    batch
    .describe_compute_environments(
        computeEnvironments=[compute_environment_name]
    )
    ['computeEnvironments']
)



if args.action == "create":
    
    try:
        batch.create_compute_environment(
            computeEnvironmentName = compute_environment_name,
            type = "MANAGED",
            serviceRole = f"AWSBatchServiceRole",
            computeResources = {
                "type" : "FARGATE_SPOT",
                "maxvCpus" : 2,
                "subnets" : [args.subnet],
                "securityGroupIds" : [args.security_group]
            }
        )
        print(f"Created compute environment for '{args.name}'")
        
    except ClientError:
        try:
            update_compute_environment_status("ENABLED")
        except ClientError:
            pass
    
    wait_for_compute_environment_status('ENABLED')
    
    sleep(1)
    
    try:
        batch.create_job_queue(
            jobQueueName=job_queue_name,
            priority=1,
            computeEnvironmentOrder=[ { 'order': 1, 'computeEnvironment': compute_environment_name } ]
        )
        print(f"Job queue {job_queue_name} created")
    except ClientError: pass
    
    
    try:
        
        response = iam.create_role(
            RoleName=batch_execution_role_name,
            AssumeRolePolicyDocument='{"Version":"2008-10-17","Statement":[{"Sid":"","Effect":"Allow","Principal":{"Service":"ecs-tasks.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
        )
         
        batch_execution_role_arn = response['Arn']
        
        print(f"Execution role {batch_execution_role_name} created")
        
    except:
        
        roles = iam.list_roles()['Roles']
        
        for role in roles:
            if role['RoleName'] == batch_execution_role_name:
                batch_execution_role_arn = role['Arn']
                break
        else:
            raise RuntimeError("Unable to create or lookup execution role, please double check your credentials")
        
        
        
    iam.attach_role_policy(
        RoleName=batch_execution_role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
    )
        
    
    try:
        
        job_definitions = batch.describe_job_definitions(jobDefinitionName=job_definition_name)['jobDefinitions']
        
        if job_definitions:
            if (
                input("Launch a new revision of the job definition? [y/N]: ").lower() + ' '
            )[0] != 'y':
                print('No action taken.')
                exit(0)
        
        response = batch.register_job_definition(
            jobDefinitionName = job_definition_name,
            type = 'container',
            parameters = {},
            containerProperties = {
                'image': 'nrel/bifacial_radiance:latest',
                'command': [],
                'jobRoleArn': '',
                'executionRoleArn': batch_execution_role_arn,
                'volumes': [],
                'environment': [],
                'mountPoints': [],
                'readonlyRootFilesystem': False,
                'privileged': False,
                'ulimits': [],
                'user': '',
                'resourceRequirements': [
                    {'value':'1','type':'VCPU'},
                    {'value':'2048','type':'MEMORY'},
                ],
                'linuxParameters': {},
                # 'logConfiguration': {},
                'secrets': [],
                'networkConfiguration': { 'assignPublicIp': 'DISABLED' },
                'fargatePlatformConfiguration': { 'platformVersion': '1.4.0' }
            },
            propagateTags = True,
            timeout = {'attemptDurationSeconds': 900},
            tags = {},
            platformCapabilities = ['FARGATE']
        )
        
        print(f"Registered job definition '{job_definition_name}' revision #{response['revision']}")
        print("\nLaunch a job using the latest job definition:\n")
        print(f"https://{args.region}.console.aws.amazon.com/batch/v2/home?region={args.region}#job-definition/detail/arn:aws:batch:{args.region}:{account_id}:job-definition/{job_definition_name}:{response['revision']}")
        
        
    except ClientError: pass
    
    
    

if args.action == "delete":
    
    """Not necessary but this will deregister all past job-definitions in the given namespace"""
    # job_definitions = batch.describe_job_definitions(jobDefinitionName=job_definition_name)['jobDefinitions']
    # for job_definition in job_definitions:
    #     job_definition_revision = f"{job_definition_name}:{job_definition['revision']}"
    #     response = (batch.deregister_job_definition(jobDefinition = job_definition_revision))
    #     print(f"Deregistered {job_definition_revision}")
    
    try:
        iam.detach_role_policy(
            RoleName=batch_execution_role_name,
            PolicyArn="arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == 'NoSuchEntity':
            pass
        else:
            raise(e)
    
    try:
        iam.delete_role(RoleName=batch_execution_role_name)
        print(f"Execution role {batch_execution_role_name} deleted")
    except ClientError as e:
        if e.response["Error"]["Code"] == 'NoSuchEntity':
            pass
        else:
            raise(e)
            
    try:
        batch.update_job_queue( jobQueue=job_queue_name, state='DISABLED' )
    except ClientError as e:
        if e.response["Error"]["Code"] == 'ClientException':
            pass
        else:
            raise(e)
    
    batch.describe_job_queues(jobQueues=['bifacial-radiance-job-queue'])
    
    batch.delete_job_queue(jobQueue=job_queue_name)
    

    status = get_compute_environment_status()
        
    
    print(f"Disabling '{compute_environment_name}' ")
    batch.update_compute_environment(
        computeEnvironment = compute_environment_name,
        state="DISABLED"
    )
    
    wait_for_compute_environment_status('DISABLED')

    try:
        batch.delete_compute_environment(computeEnvironment = compute_environment_name)
        print(f"Compute environment '{compute_environment_name}' marked for deletion")
    except ClientError as e:
        if e.response["Error"]["Code"] == 'ClientException':
            pass
        else:
            raise(e)
    