#!/bin/bash
aws cloudformation list-exports --region $AWS_DEFAULT_REGION > exports.json
VPCID=$(cat exports.json | jq -r '.Exports[] | select(.Name | contains ("VPC")) | .Value')
rm exports.json
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/rbac-role.yaml
curl https://raw.githubusercontent.com/kubernetes-sigs/aws-alb-ingress-controller/v1.1.8/docs/examples/alb-ingress-controller.yaml | 
sed "s/# - --cluster-name=devCluster/- --cluster-name=cluster/;s/# - --aws-region=us-west-1/- --aws-region=$AWS_DEFAULT_REGION/" |
sed "s/# - --aws-vpc-id=vpc-xxxxxx/- --aws-vpc-id=$VPCID/" |
kubectl apply -f -