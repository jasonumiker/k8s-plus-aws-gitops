# Creation of required Kubernetes infrastructure

This installs:
* The ALB Ingress Controller
* The External DNS Controller
* The External Secrets Controller
* Sets up the required ExternalSecrets object to retrieve the RDS secret and upsert it into the cluster

Most of the items in this folder are provisioned as part of the EnvironmentStack's CodeBuild job described in the `buildspec.yml` in the aws-infrastructure folder (the same one that provisions EKS).

The steps that goes through are:
1. `./install-alb-ingress.sh`
1. `kubectl apply -f ghost-namespace.yaml`
1. `kubectl apply -f externaldns.yaml`
1. `./install-flux.sh`
1. `./update-ghost-external-secret.sh`
1. `./install-external-secrets.sh`
1. `kubectl apply -f ghost-externalsecret.yaml`

And the pre-reqs to be able to run these commands within Amazon Linux are in `./install-prereqs.sh`.