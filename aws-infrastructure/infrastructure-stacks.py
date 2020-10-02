from aws_cdk import (
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ec2 as ec2,
    aws_eks as eks,
    aws_elasticloadbalancingv2 as elbv2,
    core
)
import os

class AWSInfrastructureStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        eks_vpc = ec2.Vpc(
            self, "VPC",
            cidr="10.0.0.0/16"
        )

        # Create IAM Role For code-server bastion
        bastion_role = iam.Role(
            self, "BastionRole",
            assumed_by=iam.CompositePrincipal(
                iam.ServicePrincipal("ec2.amazonaws.com"),
                iam.AccountRootPrincipal()
            ),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")
            ]
        )
        self.bastion_role = bastion_role
        # Create EC2 Instance Profile for that Role
        instance_profile = iam.CfnInstanceProfile(
            self, "InstanceProfile",
            roles=[bastion_role.role_name]            
        )

        # Create SecurityGroup for the Control Plane ENIs
        eks_security_group = ec2.SecurityGroup(
            self, "EKSSecurityGroup",
            vpc=eks_vpc,
            allow_all_outbound=True
        )
        
        eks_security_group.add_ingress_rule(
            ec2.Peer.ipv4('10.0.0.0/16'),
            ec2.Port.all_traffic()
        )    

        # Create an EKS Cluster
        eks_cluster = eks.Cluster(
            self, "cluster",
            vpc=eks_vpc,
            masters_role=bastion_role,
            default_capacity_type=eks.DefaultCapacityType.NODEGROUP,
            default_capacity_instance=ec2.InstanceType("m5.large"),
            default_capacity=2,
            security_group=eks_security_group,
            endpoint_access=eks.EndpointAccess.PUBLIC_AND_PRIVATE,
            version=eks.KubernetesVersion.V1_17
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
                "clusterName": eks_cluster.cluster_name,
                "awsRegion": self.region,
                "awsVpcID": eks_vpc.vpc_id,
                "rbac": {
                    "create": True,
                    "serviceAccount": {
                        "create": False,
                        "name": "alb-ingress-controller"
                    }
                }
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
                "provider": "aws",
                "aws": {
                    "region": self.region
                },
                "serviceAccount": {
                    "create": False,
                    "name": "external-dns"
                },
                "podSecurityContext": {
                    "fsGroup": 65534
                }
            }
        )    

        # Install external secrets controller
        # Create the Service Account
        externalsecrets_service_account = eks_cluster.add_service_account(
            "kubernetes-external-secrets",
            name="kubernetes-external-secrets",
            namespace="kube-system"
        )

        # Define the policy in JSON
        externalsecrets_policy_statement_json_1 = {
        "Effect": "Allow",
            "Action": [
                "secretsmanager:GetResourcePolicy",
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "secretsmanager:ListSecretVersionIds"
            ],
            "Resource": [
                "*"
            ]
        }

        # Add the policies to the service account
        externalsecrets_service_account.add_to_policy(iam.PolicyStatement.from_json(externalsecrets_policy_statement_json_1))

        # Deploy the Helm Chart
        eks_cluster.add_chart(
            "external-secrets",
            chart="kubernetes-external-secrets",
            repository="https://godaddy.github.io/kubernetes-external-secrets/",
            namespace="kube-system",
            values={
                "env": {
                    "AWS_REGION": self.region
                },
                "serviceAccount": {
                    "name": "kubernetes-external-secrets",
                    "create": False
                },
                "securityContext": {
                    "fsGroup": 65534
                }
            }
        )

        # Deploy Flux
        # Deploy the Helm Chart
        eks_cluster.add_chart(
            "flux",
            chart="flux",
            repository="https://charts.fluxcd.io",
            namespace="kube-system",
            values={
                "git": {
                    "url": "git@github.com:jasonumiker/k8s-plus-aws-gitops",
                    "path": "k8s-app-resources",
                    "branch": "cdk-for-cluster"
                }
            }
        )        

        # Create code-server bastion
        # Get Latest Amazon Linux AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
            )

        # Create SecurityGroup for code-server
        security_group = ec2.SecurityGroup(
            self, "SecurityGroup",
            vpc=eks_vpc,
            allow_all_outbound=True
        )
        
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(8080)
        )

        # Create our EC2 instance running CodeServer
        code_server_instance = ec2.Instance(
            self, "CodeServerInstance",
            instance_type=ec2.InstanceType("t3.large"),
            machine_image=amzn_linux,
            role=bastion_role,
            vpc=eks_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=security_group,
            block_devices=[ec2.BlockDevice(device_name="/dev/xvda", volume=ec2.BlockDeviceVolume.ebs(20))]
        )

        # Add UserData
        code_server_instance.user_data.add_commands("mkdir -p ~/.local/lib ~/.local/bin ~/.config/code-server")
        code_server_instance.user_data.add_commands("curl -fL https://github.com/cdr/code-server/releases/download/v3.5.0/code-server-3.5.0-linux-amd64.tar.gz | tar -C ~/.local/lib -xz")
        code_server_instance.user_data.add_commands("mv ~/.local/lib/code-server-3.5.0-linux-amd64 ~/.local/lib/code-server-3.5.0")
        code_server_instance.user_data.add_commands("ln -s ~/.local/lib/code-server-3.5.0/bin/code-server ~/.local/bin/code-server")
        code_server_instance.user_data.add_commands("echo \"bind-addr: 0.0.0.0:8080\" > ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"auth: password\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"password: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("echo \"cert: false\" >> ~/.config/code-server/config.yaml")
        code_server_instance.user_data.add_commands("~/.local/bin/code-server &")
        code_server_instance.user_data.add_commands("yum -y install jq gettext bash-completion moreutils")
        code_server_instance.user_data.add_commands("sudo pip install --upgrade awscli && hash -r")
        code_server_instance.user_data.add_commands("echo 'export ALB_INGRESS_VERSION=\"v1.1.8\"' >>  ~/.bash_profile")
        code_server_instance.user_data.add_commands("curl --silent --location -o /usr/local/bin/kubectl \"https://amazon-eks.s3.us-west-2.amazonaws.com/1.17.9/2020-08-04/bin/linux/amd64/kubectl\"")
        code_server_instance.user_data.add_commands("chmod +x /usr/local/bin/kubectl")
        code_server_instance.user_data.add_commands("curl -L https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash")
        code_server_instance.user_data.add_commands("export ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)")
        code_server_instance.user_data.add_commands("export AWS_REGION=$(curl -s 169.254.169.254/latest/dynamic/instance-identity/document | jq -r '.region')")
        code_server_instance.user_data.add_commands("echo \"export ACCOUNT_ID=${ACCOUNT_ID}\" | tee -a ~/.bash_profile")
        code_server_instance.user_data.add_commands("echo \"export AWS_REGION=${AWS_REGION}\" | tee -a ~/.bash_profile")
        code_server_instance.user_data.add_commands("aws configure set default.region ${AWS_REGION}")
        code_server_instance.user_data.add_commands("curl --silent --location https://rpm.nodesource.com/setup_12.x | bash -")
        code_server_instance.user_data.add_commands("yum -y install nodejs")
        code_server_instance.user_data.add_commands("amazon-linux-extras enable python3")
        code_server_instance.user_data.add_commands("yum install -y python3 --disablerepo amzn2-core")
        code_server_instance.user_data.add_commands("yum install -y git")        
        code_server_instance.user_data.add_commands("rm /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python && ln -s /usr/bin/pip3 /usr/bin/pip")
        code_server_instance.user_data.add_commands("npm install -g aws-cdk")
        code_server_instance.user_data.add_commands("echo 'export KUBECONFIG=~/.kube/config' >>  ~/.bash_profile")

        # Add ALB
        lb = elbv2.ApplicationLoadBalancer(
            self, "LB",
            vpc=eks_vpc,
            internet_facing=True
        )
        listener = lb.add_listener("Listener", port=80)
        listener.connections.allow_default_port_from_any_ipv4("Open to the Internet")
        listener.connections.allow_to_any_ipv4(port_range=ec2.Port(string_representation="TCP 8080", protocol=ec2.Protocol.TCP, from_port=8080, to_port=8080))
        listener.add_targets("Target", port=8080, targets=[elbv2.InstanceTarget(
            instance_id=code_server_instance.instance_id,
            port=8080
        )])

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
env = core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"])
aws_infrastructure_stack = AWSInfrastructureStack(app, "AWSInfrastructureStack", env=env)
resources_pipeline_stack = AWSAppResourcesPipeline(app, "ResourcesPipelineStack", env=env)
app.synth()
