# CDK to create a MySQL RDS database for Ghost to use

from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
    core,
)
import os

class GhostDBStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, 'VPC', vpc_name="VPC")

        security_group = ec2.SecurityGroup(
            self, "Ghost-DB-SG",
            vpc=vpc,
            allow_all_outbound=True
        )
        
        security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.tcp(3306)
        )

        rds.DatabaseInstance(
            self, "RDS",
            deletion_protection=False,
            removal_policy=core.RemovalPolicy.DESTROY,
            multi_az=False,
            allocated_storage=20,
            engine=rds.DatabaseInstanceEngine.MYSQL,
            engine_version="8.0.16",
            master_username="root",
            database_name="ghost",
            vpc=vpc,
            instance_class=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            security_groups=[security_group]
        )

app = core.App()
env = core.Environment(account=os.environ.get('CDK_DEPLOY_ACCOUNT'), region=os.environ.get('AWS_DEFAULT_REGION'))
GhostDBStack(app, "GhostDBStack", env=env)
app.synth()