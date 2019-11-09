# An exmaple approach for Kubernetes and AWS GitOps

This is a prototype for an approach for GitOps that covers both AWS and Kubernetes that enables the straightforward use of the the best tools and managed services across both. 

It representts the AWS-specific resources (such as VPCs and databases) via CDK/CloudFormation in one set of folders (one for base infrastructure that changes rarely and one for the application-speific backing resources that would change more often) and the same for the Kubernetes equivilents.

The folder structure is:

```
k8s-plus-aws-gitops/
  - aws-infrastructure/ for the AWS-specific infrastructure resources (VPC, EKS cluster, etc.)
  - aws-app-resources/ for the AWS and application-specific resources (databases, caches, queues, etc.)
  - k8s-infrastructure/ for the Kubernetes-specific infrastrucutre resources (Namespaces, RBAC, Prometheus, etc.)
  - k8s-app-resources: for the Kubernetes and application-specific resources (Deployments, Services, etc.)
  - dockerbuild: for the Dockerfile(s) and associated items required to build the app into a container such as the CodeBuild buildspec.yml(s)
````