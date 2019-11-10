Once flux is deployed things in this folder will be deployed to the cluster and any changes will subsequently be on each merge to master.

The necessary password for access to the database will be in the Kubernetes Secret ghost-database. It will be created by the external-secrets operator due to the equivilent ExternalSecret created in k8s-infrastrucutre instructing it to do so. 

What happened there is:
1. CDK created a secret in SecretsManager
1. It created the RDS instance referencing that secret as the one to use
1. The external-secrets operator looks for ExternalSecrets that tell it things it should upsert into Kubernetes - we created one for it in k8s-infrastructure.
1. From the perspective of the Deployment in Kubernetes it can just reference the Kubernetes secret with it decoupled from the AWS Secrets Manager.