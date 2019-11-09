#!/bin/bash
export AWS_DEFAULT_REGION=ap-southeast-2
chmod -R u+x *.sh
cd aws-infrastructure
./create-vpc-and-eks.sh
cd ../aws-app-resources
cdk deploy --require-approval never
cd ../k8s-infrastructure
./install-helm.sh
./install-external-secrets.sh
kubectl apply -f externaldns.yaml
cd ../k8s-app-resources
./update-external-secret.sh
kubectl apply -f ghost-namespace.yaml
kubectl apply -f ghost-externalsecret.yaml
kubectl apply -f ghost-service.yaml
kubectl apply -f ghost-deployment.yaml