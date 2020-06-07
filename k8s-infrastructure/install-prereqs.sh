#!/bin/bash

sudo curl --silent --location -o /usr/local/bin/kubectl "https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/kubectl"
sudo chmod +x /usr/local/bin/kubectl
sudo curl --silent --location -o /usr/local/bin/aws-iam-authenticator "https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/aws-iam-authenticator"
sudo chmod +x /usr/local/bin/aws-iam-authenticator
sudo curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/latest_release/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv -v /tmp/eksctl /usr/local/bin
sudo curl --silent --location -o /usr/local/bin/fluxctl "https://github.com/fluxcd/flux/releases/download/1.19.0/fluxctl_linux_amd64"
sudo chmod +x /usr/local/bin/fluxctl
sudo curl -L https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
sudo yum install jq -y
export AWS_DEFAULT_REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep -oP '\"region\"[[:space:]]*:[[:space:]]*\"\K[^\"]+')
echo export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION > ~/.bashrc
aws eks update-kubeconfig --name cluster