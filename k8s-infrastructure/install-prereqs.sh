#!/bin/bash

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