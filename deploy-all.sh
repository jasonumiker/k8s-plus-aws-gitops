#!/bin/bash
sudo curl --silent --location -o /usr/local/bin/kubectl "https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/kubectl"
sudo chmod +x /usr/local/bin/kubectl
sudo curl --silent --location -o /usr/local/bin/aws-iam-authenticator "https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/aws-iam-authenticator"
sudo chmod +x /usr/local/bin/aws-iam-authenticator
sudo curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/eksctl /usr/local/bin
sudo curl -L https://git.io/get_helm.sh | bash
sudo yum install jq -y
ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa
export AWS_DEFAULT_REGION=ap-southeast-2
chmod -R u+x *.sh
cd aws-infrastructure
./create-vpc-and-eks.sh
cd ../aws-app-resources
export CDK_DEPLOY_ACCOUNT=$(aws sts get-caller-identity | jq -r '.Account')
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