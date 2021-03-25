
import pulumi
import pulumi_aws as aws
import os
import inspect
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import rds_config

#### do not create serverless, it does not allow public access, only in VPC

engine = "aurora-mysql"
engine_version = "5.7.mysql_aurora.2.07.1"

db_username = rds_config.db_username
db_password = rds_config.db_password
db_name = rds_config.db_name

ip = rds_config.my_ip

### egress is needed for lambda to function
lambda_security_group = aws.ec2.SecurityGroup("pulumi-ncbi-lambda",
    tags={
        "app": "pulumi-ncbi-lambda",
    }
)

default_security_group = aws.ec2.SecurityGroup("pulumi-ncbi", 
ingress=[aws.ec2.SecurityGroupIngressArgs(
        description = "allow Aurora",
        from_port=3306,
        to_port=3306,
        protocol="tcp",
        cidr_blocks=[f"{ip}/32"],
        security_groups = [lambda_security_group.id]
)])

allow_default_security_group = aws.ec2.SecurityGroupRule("allow_default_security_group",
    type="egress",
    to_port=3306,
    protocol="tcp",
    source_security_group_id = default_security_group.id,
    from_port=3306,
    security_group_id=lambda_security_group.id)



available_zones = aws.get_availability_zones(state="available")

default = aws.rds.Cluster("default",
    cluster_identifier="pulumi-ncbi-cluster",
    availability_zones=available_zones.names,
    database_name = db_name,
    master_username = db_username,
    master_password = db_password,
    skip_final_snapshot = True,
    engine = engine,
    engine_version = engine_version,
    vpc_security_group_ids = [default_security_group.id]
    )


### have to make it public
instance = aws.rds.ClusterInstance(f"clusterInstances-1",
        identifier="aurora-cluster-1",
        cluster_identifier=default.id,
        instance_class="db.t3.small",
        engine=engine,
        engine_version=engine_version,
        publicly_accessible = True
        )


#pulumi.export("default_security_group", default_security_group.id)

#pulumi.export('endpoint',  default.endpoint)
pulumi.export('instance-endpoint',  instance.endpoint)
#pulumi.export("lambda_security_group", lambda_security_group.id)

