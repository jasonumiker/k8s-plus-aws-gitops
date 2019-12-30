Once Flux is deployed things in this folder will be deployed to the cluster and any changes will subsequently be on each merge to master.

The necessary password for access to the database will be in the Kubernetes Secret ghost-database. It will be created by the external-secrets operator due to the equivilent ExternalSecret created in k8s-infrastructure instructing it to do so. 

What happened there is:
1. CDK created a secret in SecretsManager
1. It created the RDS instance referencing that secret as the one to use
1. The [external-secrets](https://github.com/godaddy/kubernetes-external-secrets) operator looks for ExternalSecrets that tell it things it should upsert into Kubernetes Secrets - we should have created one for it in ../k8s-infrastructure.
1. The Deployment can just reference the resulting Kubernetes Secret with it - decoupling things nicely from AWS and the Secrets Manager.

We also leverage an Ingress tied to the ALB Ingress Controller (note the AWS-specific annotations for this to work). The advantage of this is that the ALB will route traffic directly to the Pod IPs rather than via a NodePort NAT through the hosts which is much more efficient. It also means that there one fewer service to manage, and pay for the resources consumed by, on your cluster (which you would have if using something like the nginx Ingress Controller).

NOTE: If you want HTTPS you need to add the ARN of a ACM key in your account to the Ingress object.

And, finally, we use External DNS to update a CNAME to point at the ALB created/managed by the ALB Ingress.

NOTE: You need a Route53 Zone and corresponding public domain name you own that it hosts to do that part.