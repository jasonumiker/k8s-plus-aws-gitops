# Creation of required Kubernetes infrastrucutre

CDK by default stores the secrets for things like our RDS database in AWS Secrets Manager. We are going to leverage an operator for AWS Secrets Manager (https://github.com/godaddy/kubernetes-external-secrets) to be able to get those secrets in to Kubernetes to leverage within our `k8s-app-resrouces` like Ghost.

This operator is installed via a Helm chart so we need to set up Helm on the cluster and then we use that to install the operator.

## Prerequisites
The Helm CLI, eksctl and jq

## Instructions
1. Run `install-helm.sh` to install Helm's backend (Tiller) to the cluster
1. Run `install-external-secrets.sh` to install kubernetes-external-secrets (https://github.com/godaddy/kubernetes-external-secrets) to map the secret(s) for our RDS in Secrets Manager to Kubernetes secrets
1. Run `kubectl apply -f exernaldns.yaml` to install external-dns (https://github.com/kubernetes-sigs/external-dns) to allow us to automatically update a more useful Route53 CNAME to point at our random load balancer address.