# Creation of AWS VPC and EKS Cluster
This example requires an AWS VPC with public and private subnets as well as an EKS cluster. This will result in three CloudFormation Stacks - a VPC, an EKS control plane and an EKS NodeGroup (ASG of Worker Nodes) joined to that control plane.

NOTE: The IAM Role or User that runs this script will permanently 'own' and be a full cluser-admin on the resulting cluster. It is best to have this run as a dedicated role as part of a pipeline.

## Prerequisites
Have the AWS CLI, kubectl, aws-iam-authenticator, eksctl and jq installed.

## Setup Instructions
1. Set the AWS_DEFAULT_REGION environment variable to the region you want such as `export AWS_DEFAULT_REGION=ap-southeast-2`.
1. (Optional) open the `create-vpc-and-eks.sh` file and change any parameters being passed to the VPC like the CIDRs to suit your environment.
1. Run `create-vpc-and-eks.sh` to:
    1. Create a VPC from the AWS VPC QuickStart template (https://aws.amazon.com/quickstart/architecture/vpc/)
    1. Copy `cluster.yaml.orig` to `cluster.yaml` then fill in the required envirionment details from the Exports of that VPC Stack as well as the AWS_DEFAULT_REGION environment variable.
    1. Create an EKS cluster with `eksctl` from the the settings in `cluster.yaml`
1. Run `create-kubernetes-external-secrets-serviceaccount.sh` to create the service acccount to IAM role mapping to allow that service to read the secrets from AWS Secrets Manager.

## How to make changes post deployment?
1. If you wanted to change the VPC you'd update the Parameters in the deployed CloudFormation Stack
    1. NOTE - if you change things that would interfere with the EKS cluster or NodeGroups that might be problematic. CloudFormation should protect you from some of that if there are resources deployed into the VPC and the changes would be disruptive but be careful.
1. If you wanted to change the EKS then you'd use eksctl and it'd update the underlying CloudFormation stack(s) on your behalf as required.

TODO: Replace with CDK for the VPC and EKS cluster creation