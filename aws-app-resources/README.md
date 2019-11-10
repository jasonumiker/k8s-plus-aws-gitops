# Ghost Database creation using CDK / CloudFormation
The one application-specific resource here is the MySQL RDS database required as the back-end to Ghost. We'll use the CDK to generate the CloudFormation template that we need.

This will create:
* A MySQL RDS Database with the following characteristics:
    * t3.micro (the minimum instance size)
    * 20 GB of storage (the minimum storage size)
    * Single-AZ (not highly available at half the cost)
    * With the database name `ghost`
    * In a private subnet of the VPC created by `aws-infrastructure`
* A security group for the RDS that allows connections on port 3306
* The randomly-generated `root` account password stored in AWS Secrets Manager

Obviously for some of these parameters we'd change them for real production use but, for our prototype, we are going with the cheapest and fastest to privision option as it is just illustrative of the approach.

One of the nice things about the CDK is that we don't need it to have created the VPC in order to not have to specify the IDs of the subnets to use etc - we can tell it to connect to AWS and work out those details giving it just the name of the VPC (which we can keep consistent across the environments so it always works).

## Prerequisites
* You should already have created the VPC using the process in the `aws-infrastructure` folder.
* You must set the following environment variables in the environment
    * CDK_DEFAULT_ACCOUNT to the AWS account number using a command like `export CDK_DEPLOY_ACCOUNT=1111111111111` where you replace 111111111111 with your account number. 
        * If you already have your AWS IAM credentials configured with the CLI and have jq installed then you can run `export CDK_DEPLOY_ACCOUNT=$(aws sts get-caller-identity | jq -r '.Account')` instead.
    * AWS_DEFAULT_REGION to the AWS region you want to deploy to using a command like `export AWS_DEFAULT_REGION=ap-southeast-2` changing ap-southeast-2 if you want to deploy to a region other than Sydney.
        * This needs to be the same region that you deployed the VPC and EKS cluster to in the `aws-infrastructure` steps.

## How to deploy
* (Optional) Have a look at the `ghost-database.py` file to see the RDS and security group we're creating
    * Note that we don't specify a Secrets Manager secret but the CDK will default to creating one with a random password then using it to provision the RDS for us.
* Run `cdk synth` to generate the `cdk.out/GhostDBStack.template.json` template file
* (Optional) Have a look at the `cdk.out/GhostDBStack.template.json` template fie - this is the CloudFormation that CDK is about to deploy to our account.
* Run `cdk deploy --require-approval never` to deloy this required RDS to our account and VPC

## (Optional) How to deploy via CodeBuild
There is a buildspec.yml file in the folder which instructs CodeBuild to deploy this on your behalf. A pipeline watching this repo for changes and then invokes that CodeBuild job is in the ../aws-infrastrucuture folder.