import sagemaker
from sagemaker import image_uris
import boto3
import os
import time
import json
from pathlib import Path
from sagemaker.utils import name_from_base

####********Imports and Variables***********#####
sagemaker_session = sagemaker.Session()

role = sagemaker.get_execution_role()  # execution role for the endpoint
sess = sagemaker.session.Session()  # sagemaker session for interacting with different AWS APIs
bucket = sess.default_bucket()  # bucket to house artifacts
model_bucket = sess.default_bucket()  # bucket to house artifacts
s3_code_prefix_deepspeed = "sm_lmi_llm/$model_base_name/deepspeed"  # folder within bucket where code artifact will go

region = sess._region_name
account_id = sess.account_id()

s3_client = boto3.client("s3")
sm_client = boto3.client("sagemaker")
smr_client = boto3.client("sagemaker-runtime")


s3_code_artifact_deepspeed = sess.upload_data("model.tar.gz", bucket, s3_code_prefix_deepspeed)
# print(f"S3 Code or Model tar for deepspeed uploaded to --- > {s3_code_artifact_deepspeed}")

####********Define Serving Container ***********#####

# inference_image_uri = f"{account_id}.dkr.ecr.{region}.amazonaws.com/djl-ds:latest"
inference_image_uri = sagemaker.image_uris.retrieve(
    "djl-$engine", region=region, version="$ds_version"
)
# print(f"Image going to be used is ---- > {inference_image_uri}")


def main():
    ####********Create SM Model and Endpoint ***********#####
    
    model_name_ds = name_from_base(f"$model_base_name-model-ds")
    print(model_name_ds)


    create_model_response = sm_client.create_model(
        ModelName=model_name_ds,
        ExecutionRoleArn=role,
        PrimaryContainer={"Image": inference_image_uri, "ModelDataUrl": s3_code_artifact_deepspeed},
    )
    model_arn = create_model_response["ModelArn"]

    # print(f"Created Model: {model_arn}")

    model_name = model_name_ds
    # print(f"Building EndpointConfig and Endpoint for: {model_name}")

    endpoint_config_name = f"{model_name}-config"
    endpoint_name = f"{model_name}-endpoint"
    bucket_prefix='$bucket_prefix'

    ####********Create SM Endpoint config***********#####

    endpoint_config_response = sm_client.create_endpoint_config(
        EndpointConfigName=endpoint_config_name,
        AsyncInferenceConfig={
            "ClientConfig": { 
             "MaxConcurrentInvocationsPerInstance": $MaxConcurrentInvocationsPerInstance},
            "OutputConfig": { 
                "S3OutputPath": f"s3://{bucket}/{bucket_prefix}/output"}
        },
        ProductionVariants=[
            {
                "VariantName": "variant1",
                "ModelName": model_name,
                "InstanceType": "$InstanceType",
                "InitialInstanceCount": 1,
                "ModelDataDownloadTimeoutInSeconds": 3600,
                "ContainerStartupHealthCheckTimeoutInSeconds": 3600,
                # "VolumeSizeInGB": 512
            },
        ],
    )
    endpoint_config_response

    ####********Deploy SM Endpoint***********#####
    create_endpoint_response = sm_client.create_endpoint(
        EndpointName=f"{endpoint_name}", 
        EndpointConfigName=endpoint_config_name
    )
    # print(f"Created Endpoint: {create_endpoint_response['EndpointArn']}")

    return create_endpoint_response['EndpointArn']

if __name__ == "__main__":
    main()
    