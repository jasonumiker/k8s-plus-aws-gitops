# Creation of AWS VPC, EKS Cluster and GitOps CodePipeline for aws-app-resources
This folder has two CDK stacks:

1. The `EnvironmentStack` which creates:
    1. The AWS VPC
    1. An IAM Role dedicated to cluster creation/administration to own the cluster
    1. An EKS cluster (by running `eksctl` within `CodeBuild` based on the `buildspec.yml` and `cluster.yaml`)
    1. A Cloud9 with that IAM Role assigned to serve as a bastion/jumpbox.
1. The `ResourcesPipelineStack` which create a CI/CD pipeline to provision, and update based on any changes to the content of, the aws-app-resources folder.

Both stacks are defined in the `infrastrucutre-stacks.py` Python CDK file. If you don't want to install CDK to deploy I have taken the two CloudFormation templates it generates - `EnvironmentStack.template.json` and `ResourcesPipelineStack.template.json` - and put them in the folder ready for a standard CloudFormation Deployment as well.

These stacks can be deployed into any region that supports both EKS in Fargate Mode as well as Cloud9.

Note that the EnvironmentStack is not idempotent and it cannot be deployed a second time after it's creation. This is because it calls `eksctl` via CodeBuild in a configuration that will fail on re-run. As such I configure the CodePipline to do one initial run on creation then only re-run if invoked manually rather than true GitOps.

I am investigating how to make this true GitOps as well - but will likely just wait until CDK can support everything I need directly (it is currently experimental in CDK atm and I couldn't make it work yet was very familiar with eksctl so went that way) then refactor it to be all CDK.