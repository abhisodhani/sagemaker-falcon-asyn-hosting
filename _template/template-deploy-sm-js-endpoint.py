from sagemaker.jumpstart.model import JumpStartModel
import sagemaker
from sagemaker.utils import name_from_base
from sagemaker.async_inference.async_inference_config import AsyncInferenceConfig

####********Imports and Variables***********#####
sess = sagemaker.session.Session() 
s3_bucket = sess.default_bucket()  # bucket to house artifacts
bucket_prefix = "$bucket_prefix"  # folder within bucket where code artifact will go
model_id = "$model_id"
endpoint_name=name_from_base("$model_base_name-sm-js")
print(endpoint_name)

def main():
    async_config = AsyncInferenceConfig(
        output_path=f"s3://{s3_bucket}/{bucket_prefix}/output",
        max_concurrent_invocations_per_instance=$MaxConcurrentInvocationsPerInstance
    )
    ####********Create SM Model and deploy Endpoint ***********#####
    
    model = JumpStartModel(model_id=model_id)
    create_endpoint_response = model.deploy(
            initial_instance_count=$InstanceCount,
            instance_type="$InstanceType",
            endpoint_name=endpoint_name,
            async_inference_config=async_config)

    return create_endpoint_response['EndpointArn']

if __name__ == "__main__":
    main()
    