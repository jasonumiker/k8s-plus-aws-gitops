#!/bin/bash
aws cloudformation create-stack \
--template-url https://aws-quickstart.s3.amazonaws.com/quickstart-aws-vpc/templates/aws-vpc.template \
--stack-name VPC \
--parameters ParameterKey=AvailabilityZones,ParameterValue="${AWS_DEFAULT_REGION}a\,${AWS_DEFAULT_REGION}b\,${AWS_DEFAULT_REGION}c" \
ParameterKey=NumberOfAZs,ParameterValue=3 ParameterKey=CreateAdditionalPrivateSubnets,ParameterValue=false \
ParameterKey=CreatePrivateSubnets,ParameterValue=true ParameterKey=PrivateSubnet1ACIDR,ParameterValue=10.0.0.0/19 \
ParameterKey=PrivateSubnet2ACIDR,ParameterValue=10.0.32.0/19 ParameterKey=PrivateSubnet3ACIDR,ParameterValue=10.0.64.0/19 \
ParameterKey=PublicSubnet1CIDR,ParameterValue=10.0.128.0/20 ParameterKey=PublicSubnet2CIDR,ParameterValue=10.0.144.0/20 \
ParameterKey=PublicSubnet3CIDR,ParameterValue=10.0.160.0/20 ParameterKey=VPCCIDR,ParameterValue=10.0.0.0/16 \
ParameterKey=PrivateSubnetATag2,ParameterValue=kubernetes.io/role/internal-elb=1 \
ParameterKey=PublicSubnetTag2,ParameterValue=kubernetes.io/role/elb=1
aws cloudformation wait stack-create-complete --stack-name VPC
cp cluster.yaml.orig cluster.yaml
aws cloudformation list-exports > exports.json
PrivateSubnet1AID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PrivateSubnet1AID")) | .Value')
PrivateSubnet2AID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PrivateSubnet2AID")) | .Value')
PrivateSubnet3AID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PrivateSubnet3AID")) | .Value')
PublicSubnet1ID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PublicSubnet1ID")) | .Value')
PublicSubnet2ID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PublicSubnet2ID")) | .Value')
PublicSubnet3ID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("PublicSubnet3ID")) | .Value')
sed -i "s/Quick-Start-VPC-PrivateSubnet1AID/$PrivateSubnet1AID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PrivateSubnet2AID/$PrivateSubnet2AID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PrivateSubnet3AID/$PrivateSubnet3AID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PublicSubnet1ID/$PublicSubnet1ID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PublicSubnet2ID/$PublicSubnet2ID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PublicSubnet3ID/$PublicSubnet3ID/g" cluster.yaml
sed -i "s/Quick-Start-VPC-PublicSubnet3ID/$PublicSubnet3ID/g" cluster.yaml
sed -i "s/AWS_DEFAULT_REGION/$AWS_DEFAULT_REGION/g" cluster.yaml
rm exports.json
eksctl create cluster -f cluster.yaml
eksctl utils associate-iam-oidc-provider --name cluster --approve