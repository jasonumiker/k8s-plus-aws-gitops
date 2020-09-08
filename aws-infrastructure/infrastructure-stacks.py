from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ec2 as ec2,
    aws_cloud9 as cloud9,
    aws_eks as eks,
    core
)

class AWSInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eks_vpc = ec2.Vpc(
            self, "VPC",
            cidr="10.0.0.0/16"
        )

        # Create IAM Role For CodeBuild and Cloud9
        codebuild_role = iam.Role(
            self, "BuildRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("codebuild.amazonaws.com"),
                iam.ServicePrincipal("ec2.amazonaws.com")
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )

        # Create EC2 Instance Profile for that Role
        instance_profile = iam.CfnInstanceProfile(
            self, "InstanceProfile",
            roles=[codebuild_role.role_name]            
        )

        # Create an EKS Cluster
        eks_cluster = eks.Cluster(
            self, "cluster",
            cluster_name="cluster",
            vpc=eks_vpc,
            masters_role=codebuild_role,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity_instance=ec2.InstanceType("m5.large"),
            default_capacity=2,
            version=eks.KubernetesVersion.V1_17
        )

        # Prereq for Cloud 9 to pre-clone our GitHub Repo
        cloud9_repository = cloud9.CfnEnvironmentEC2.RepositoryProperty(
            path_component="k8s-plus-aws-gitops",
            repository_url="https://github.com/jasonumiker/k8s-plus-aws-gitops"
        )

        # Create a Cloud 9 in the same VPC as the EKS Cluster
        cloud9_instance = cloud9.CfnEnvironmentEC2(
            self, "Cloud9Instance",
            instance_type="t3.micro",
            automatic_stop_time_minutes=60,
            subnet_id=eks_vpc.public_subnets[0].subnet_id,
            repositories=[cloud9_repository]
        )

        # Deploy ALB Ingress Controller

        # Create the k8s Service account and corresponding IAM Role mapped via IRSA
        alb_service_account = eks_cluster.add_service_account(
            "alb-ingress-controller",
            name="alb-ingress-controller",
            namespace="kube-system"
        )

        # Create the PolicyStatements to attach to the role
        # I couldn't find a way to get this to work with a PolicyDocument and there are 10 of these
        alb_policy_statement_json_1 = {
            "Effect": "Allow",
            "Action": [
                "acm:DescribeCertificate",
                "acm:ListCertificates",
                "acm:GetCertificate"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_2 = {
            "Effect": "Allow",
            "Action": [
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateSecurityGroup",
                "ec2:CreateTags",
                "ec2:DeleteTags",
                "ec2:DeleteSecurityGroup",
                "ec2:DescribeAccountAttributes",
                "ec2:DescribeAddresses",
                "ec2:DescribeInstances",
                "ec2:DescribeInstanceStatus",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeSecurityGroups",
                "ec2:DescribeSubnets",
                "ec2:DescribeTags",
                "ec2:DescribeVpcs",
                "ec2:ModifyInstanceAttribute",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ec2:RevokeSecurityGroupIngress"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_3 = {
            "Effect": "Allow",
            "Action": [
                "elasticloadbalancing:AddListenerCertificates",
                "elasticloadbalancing:AddTags",
                "elasticloadbalancing:CreateListener",
                "elasticloadbalancing:CreateLoadBalancer",
                "elasticloadbalancing:CreateRule",
                "elasticloadbalancing:CreateTargetGroup",
                "elasticloadbalancing:DeleteListener",
                "elasticloadbalancing:DeleteLoadBalancer",
                "elasticloadbalancing:DeleteRule",
                "elasticloadbalancing:DeleteTargetGroup",
                "elasticloadbalancing:DeregisterTargets",
                "elasticloadbalancing:DescribeListenerCertificates",
                "elasticloadbalancing:DescribeListeners",
                "elasticloadbalancing:DescribeLoadBalancers",
                "elasticloadbalancing:DescribeLoadBalancerAttributes",
                "elasticloadbalancing:DescribeRules",
                "elasticloadbalancing:DescribeSSLPolicies",
                "elasticloadbalancing:DescribeTags",
                "elasticloadbalancing:DescribeTargetGroups",
                "elasticloadbalancing:DescribeTargetGroupAttributes",
                "elasticloadbalancing:DescribeTargetHealth",
                "elasticloadbalancing:ModifyListener",
                "elasticloadbalancing:ModifyLoadBalancerAttributes",
                "elasticloadbalancing:ModifyRule",
                "elasticloadbalancing:ModifyTargetGroup",
                "elasticloadbalancing:ModifyTargetGroupAttributes",
                "elasticloadbalancing:RegisterTargets",
                "elasticloadbalancing:RemoveListenerCertificates",
                "elasticloadbalancing:RemoveTags",
                "elasticloadbalancing:SetIpAddressType",
                "elasticloadbalancing:SetSecurityGroups",
                "elasticloadbalancing:SetSubnets",
                "elasticloadbalancing:SetWebAcl"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_4 = {
            "Effect": "Allow",
            "Action": [
                "iam:CreateServiceLinkedRole",
                "iam:GetServerCertificate",
                "iam:ListServerCertificates"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_5 = {
            "Effect": "Allow",
            "Action": [
                "cognito-idp:DescribeUserPoolClient"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_6 = {
            "Effect": "Allow",
            "Action": [
                "waf-regional:GetWebACLForResource",
                "waf-regional:GetWebACL",
                "waf-regional:AssociateWebACL",
                "waf-regional:DisassociateWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_7 = {
            "Effect": "Allow",
            "Action": [
                "tag:GetResources",
                "tag:TagResources"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_8 = {
            "Effect": "Allow",
            "Action": [
                "waf:GetWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_9 = {
            "Effect": "Allow",
            "Action": [
                "wafv2:GetWebACL",
                "wafv2:GetWebACLForResource",
                "wafv2:AssociateWebACL",
                "wafv2:DisassociateWebACL"
            ],
            "Resource": "*"
        }
        alb_policy_statement_json_10 = {
            "Effect": "Allow",
            "Action": [
                "shield:DescribeProtection",
                "shield:GetSubscriptionState",
                "shield:DeleteProtection",
                "shield:CreateProtection",
                "shield:DescribeSubscription",
                "shield:ListProtections"
            ],
            "Resource": "*"
        }
        
        # Attach the necessary permissions
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_1))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_2))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_3))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_4))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_5))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_6))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_7))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_8))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_9))
        alb_service_account.add_to_policy(iam.PolicyStatement.from_json(alb_policy_statement_json_10))

        # Deploy the ALB Ingress Controller from the Helm chart
        eks_cluster.add_chart(
            "aws-alb-ingress-controller",
            chart="aws-alb-ingress-controller",
            repository="http://storage.googleapis.com/kubernetes-charts-incubator",
            namespace="kube-system",
            values={
                "autoDiscoverAwsRegion": "true",
                "autoDiscoverAwsVpcID": "true",
                "clusterName": "cluster",
                "rbac.create": "true",
                "rbac.serviceAccountName": "alb-ingress-controller"
            }
        )

        # Deploy External DNS Controller
        # Create the k8s Service account and corresponding IAM Role mapped via IRSA
        externaldns_service_account = eks_cluster.add_service_account(
            "external-dns",
            name="external-dns",
            namespace="kube-system"
        )

        # Create the PolicyStatements to attach to the role
        # I couldn't find a way to get this to work with a PolicyDocument and there are 10 of these
        externaldns_policy_statement_json_1 = {
        "Effect": "Allow",
            "Action": [
                "route53:ChangeResourceRecordSets"
            ],
            "Resource": [
                "arn:aws:route53:::hostedzone/*"
            ]
        }
        externaldns_policy_statement_json_2 = {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListResourceRecordSets"
            ],
            "Resource": [
                "*"
            ]
        }

        # Add the policies to the service account
        externaldns_service_account.add_to_policy(iam.PolicyStatement.from_json(externaldns_policy_statement_json_1))
        externaldns_service_account.add_to_policy(iam.PolicyStatement.from_json(externaldns_policy_statement_json_2))

        # Deploy the Helm Chart
        eks_cluster.add_chart(
            "external-dns",
            chart="external-dns",
            repository="https://charts.bitnami.com/bitnami",
            namespace="kube-system",
            values={
                "serviceAccount.create": "false",
                "serviceAccount.name": "external-dns"
            }
        )        

        # Deploy External Secrets Controller
        # Create the k8s Service account and corresponding IAM Role mapped via IRSA
        externalsecrets_service_account = eks_cluster.add_service_account(
            "kubernetes-external-secrets",
            name="kubernetes-external-secrets",
            namespace="kube-system"
        )

        externalsecrets_service_account.role.add_managed_policy(
            iam.ManagedPolicy.from_managed_policy_arn(
                self, "SecretsManagerReadWrite",
                managed_policy_arn="arn:aws:iam::aws:policy/SecretsManagerReadWrite")
        )

        # Deploy the Helm Chart
        eks_cluster.add_chart(
            "kubernetes-external-secrets",
            chart="kubernetes-external-secrets",
            repository="https://godaddy.github.io/kubernetes-external-secrets/",
            namespace="kube-system",
            values={
                "serviceAccount.create": "false",
                "serviceAccount.name": "kubernetes-external-secrets",
            }
        )      

        # Deploy Flux for k8s-app-resources
#        eks_cluster.add_chart(
#           "flux",
#            chart="flux",
#            repository="https://charts.fluxcd.io",
#            namespace="flux",
#            values={
#                "git.url": "git@github.com:jasonumiker/k8s-plus-aws-gitops",
#                "git.path": "k8s-app-resources",
#                "git.readonly": "true",
#                "git.branch": "cdk-for-cluster",
#                "namespace": "flux"
#            }
#        )

class AWSAppResourcesPipeline(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create IAM Role For CodeBuild
        codebuild_role = iam.Role(
            self, "BuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )

        # Create CodeBuild PipelineProject
        build_project = codebuild.PipelineProject(
            self, "BuildProject",
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename("aws-app-resources/buildspec.yml")
        )

        # Create CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "Pipeline"
        )

        # Create Artifact
        artifact = codepipeline.Artifact()

        # Add Source Stage
        pipeline.add_stage(
            stage_name="Source",
            actions=[
                codepipeline_actions.GitHubSourceAction(
                    action_name="SourceCodeRepo",
                    owner="jasonumiker",
                    repo="k8s-plus-aws-gitops",
                    output=artifact,
                    oauth_token=core.SecretValue.secrets_manager('github-token')
                )
            ]
        )

        # Add CodeBuild Stage
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                codepipeline_actions.CodeBuildAction(
                    action_name="CodeBuildProject",
                    project=build_project,
                    type=codepipeline_actions.CodeBuildActionType.BUILD,
                    input=artifact
                )
            ]
        )

app = core.App()
aws_infrastructure_stack = AWSInfrastructureStack(app, "AWSInfrastructureStack")
resources_pipeline_stack = AWSAppResourcesPipeline(app, "ResourcesPipelineStack")
app.synth()