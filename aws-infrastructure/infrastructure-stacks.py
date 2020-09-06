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

class EnvironmentStack(core.Stack):

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
            automatic_stop_time_minutes=30,
            subnet_id=eks_vpc.public_subnets[0].subnet_id,
            repositories=[cloud9_repository]
        )

        # Deploy Flux for k8s-infrastructure
        eks_cluster.add_chart(
            "flux-system",
            chart="flux",
            repository="https://charts.fluxcd.io",
            namespace="flux",
            values={
                "git.url": "git@github.com:jasonumiker/k8s-plus-aws-gitops",
                "git.path": "k8s-infrastructure",
                "git.readonly": "true",
                "git.branch": "cdk-for-cluster",
                "namespace": "flux"
            }
        )

        # Deploy Flux Helm Chart Operator for k8s-infrastructure
        eks_cluster.add_chart(
            "flux-system-helm",
            chart="helm-operator",
            repository="https://charts.fluxcd.io",
            namespace="flux",
            values={
                "namespace": "flux",
                "helm.versions": "v3",
                "git.ssh.secretName": "flux-git-deploy"
            }
        )

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
environment_stack = EnvironmentStack(app, "EnvironmentStack")
resources_pipeline_stack = AWSAppResourcesPipeline(app, "ResourcesPipelineStack")
app.synth()