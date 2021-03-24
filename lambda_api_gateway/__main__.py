"""Setup both lambda and api gateway in one go"""

import pulumi
import pulumi_aws as aws

import json
import inspect
import sys
import os

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
import rds_config

region = rds_config.region

# Create an AWS resource (S3 Bucket)
bucket = aws.s3.Bucket('sixing-lambda-bucket')

bucketObject = aws.s3.BucketObject(
    'lambda.zip',
    bucket=bucket,
    source="../database/lambda.zip"
)

# Export the name of the bucket
#pulumi.export('bucket_name', bucket.id)
#pulumi.export("lambda_zip", bucketObject.id)



role = aws.iam.Role("pyphy-pulumi-role", assume_role_policy="""{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
""")

policy_1 = aws.iam.RolePolicy("ec2",
    role=role.id,
    policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "logs:CreateLogGroup",
            "Resource": f"arn:aws:logs:{region}:456284800328:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": [
                f"arn:aws:logs:{region}:456284800328:log-group:/aws/lambda/pyphy:*"
            ]
        }
    ]
}))

policy_2 = aws.iam.RolePolicy("log",
    role=role.id,
    policy=json.dumps({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:CreateNetworkInterface",
                "ec2:DeleteNetworkInterface",
                "ec2:DescribeNetworkInterfaces"
            ],
            "Resource": "*"
        }
    ]
}))

default_vpc = aws.ec2.get_vpc(default = True)

default_subnet_ids = aws.ec2.get_subnet_ids(vpc_id=default_vpc.id)


sg = aws.ec2.get_security_group(filters = [aws.ec2.GetSecurityGroupFilterArgs(name = "tag:app", values = ["pulumi-ncbi-lambda"])
])


#pulumi.export("sg", sg)

lambda_function = aws.lambda_.Function("pyphy-pulumi",
    role = role.arn,
    runtime = "python3.6",
    description="lambda function to interact with database",
    s3_bucket = bucket.id,
    s3_key = bucketObject.id,
    handler = "lambda_function.lambda_handler",
    vpc_config = aws.lambda_.FunctionVpcConfigArgs(security_group_ids = [sg.id], subnet_ids = default_subnet_ids.ids)
)


#### without this, you will get a 500 error
allow_api_gateway = aws.lambda_.Permission("allowApiGateway",
    action="lambda:InvokeFunction",
    function=lambda_function.name,
    principal="apigateway.amazonaws.com")


#### api gateway
rest_api = aws.apigateway.RestApi("pyphy-pulumi-api", opts=pulumi.ResourceOptions(depends_on=[lambda_function]))

functions = [
                "getdictpathbytaxid",
                "getnamebytaxid",
                "gettaxidbyname",
                "getrankbytaxid",
                "getparentbytaxid",
                "getsonsbytaxid"
            ]


for index, f in enumerate(functions):
    
    resource = aws.apigateway.Resource(f"rootResource_{index}",
        rest_api=rest_api.id,
        parent_id=rest_api.root_resource_id,
        path_part=f,
        opts=pulumi.ResourceOptions(depends_on=[rest_api])
        )

    method = aws.apigateway.Method(f"method_{f}",
        rest_api=rest_api.id,
        resource_id=resource.id,
        http_method="GET",
        authorization="NONE",
        request_models={
            "application/json": "Error",
        },
        opts=pulumi.ResourceOptions(depends_on=[resource])
        )

    integration = aws.apigateway.Integration(f"Integration_{index}",
        rest_api=rest_api.id,
        resource_id=resource.id,
        http_method=method.http_method,
        integration_http_method="POST",
        type="AWS_PROXY",
        uri = lambda_function.arn.apply( lambda arn: f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations"),
        opts=pulumi.ResourceOptions(depends_on=[method, lambda_function])
        )

    response200 = aws.apigateway.MethodResponse(f"response200_{index}",
        rest_api=rest_api.id,
        resource_id=resource.id,
        http_method=method.http_method,
        status_code="200",
        opts=pulumi.ResourceOptions(depends_on=[integration])
        )


    integration_response = aws.apigateway.IntegrationResponse(f"IntegrationResponse_{index}",
        rest_api=rest_api.id,
        resource_id=resource.id,
        http_method=method.http_method,
        status_code=response200.status_code,
        response_templates={
            "application/json": "",
        },
        opts=pulumi.ResourceOptions(depends_on=[integration])
        )

api_deployment = aws.apigateway.Deployment("pyphy-deployment", stage_name = "prod", rest_api = rest_api, opts=pulumi.ResourceOptions(depends_on=[integration_response]))

pulumi.export("deployment", api_deployment.invoke_url)