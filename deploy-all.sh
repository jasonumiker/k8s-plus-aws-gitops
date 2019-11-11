#!/bin/bash
# Script to install the whole thing from an Amazon Linux instance with assigned IAM role with admin rights
sudo curl --silent --location -o /usr/local/bin/kubectl "https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/kubectl"
sudo chmod +x /usr/local/bin/kubectl
sudo curl --silent --location -o /usr/local/bin/aws-iam-authenticator "https://amazon-eks.s3-us-west-2.amazonaws.com/1.14.6/2019-08-22/bin/linux/amd64/aws-iam-authenticator"
sudo chmod +x /usr/local/bin/aws-iam-authenticator
sudo curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/eksctl /usr/local/bin
sudo curl --location -o /usr/local/bin/fluxctl "https://github.com/fluxcd/flux/releases/download/1.15.0/fluxctl_linux_amd64"
sudo chmod +x /usr/local/bin/fluxctl
sudo curl -L https://git.io/get_helm.sh | bash
sudo yum install jq -y
curl -sL https://rpm.nodesource.com/setup_12.x | sudo -E bash -
sudo yum install nodejs python37 -y
sudo npm install -g aws-cdk
sudo rm /usr/bin/python
sudo ln -s /usr/bin/python3.7 /usr/bin/python
sudo ln -s /usr/bin/pip3.7 /usr/bin/pip
sudo pip install --upgrade aws-cdk.core
ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa
export AWS_DEFAULT_REGION=ap-southeast-2
cd aws-infrastructure
chmod u+x *.sh
./create-vpc-and-eks.sh
sudo pip install --upgrade -r requirements.txt
aws secretsmanager create-secret --name github-token --secret-string "YOUR_TOKEN"
cdk deploy --require-approval never
#cd ../aws-app-resources
#export CDK_DEPLOY_ACCOUNT=$(aws sts get-caller-identity | jq -r '.Account')
#sudo pip install --upgrade -r requirements.txt
#cdk deploy --require-approval never
cd ../k8s-infrastructure
chmod u+x *.sh
./install-helm.sh
./install-flux.sh
kubectl apply -f ghost-namespace.yaml
#kubectl apply -f externaldns.yaml - requires Route53 to be set up with a 'real' domain name
./install-external-secrets.sh
./update-ghost-external-secret.sh
kubectl apply -f ghost-externalsecret.yaml
#cd ../k8s-app-resources
#kubectl apply -f ghost-service.yaml
#kubectl apply -f ghost-deployment.yaml
fluxctl --k8s-fwd-ns=flux identity
# Add the result of the above to your GitHub as an SSH key