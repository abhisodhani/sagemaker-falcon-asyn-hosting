#!/bin/bash

# Check if Python is installed
which python3
if [ $? -ne 0 ]; then
  echo "Python is not installed. Please install it before running this script."
  exit 1
fi

# Define the three options
options=( "sm-lmi" "sm-js" "hf-tgi" )

# Prompt the user for input
echo "Please select one of the following options:"
for option in "${options[@]}"
do
  echo "  $option"
done

# Read the user's input
read -p "Your selection: " selection

# Check if the user's input is valid
if [[ ! "${options[@]}" =~ "$selection" ]]; then
  echo "Invalid selection."
  exit 1
fi

# Get the path to the .properties file
properties_file="./config/${selection}.properties"

# Read all the properties from the .properties file
properties=$(cat $properties_file)

# Split the properties into an array
properties_array=($properties)

# Define the variables
variables=()

# Loop over the properties
for property in "${properties_array[@]}"
do
  # Split the property into two parts: the key and the value
  key=$(echo $property | cut -d'=' -f1)
  value=$(echo $property | cut -d'=' -f2)
  
  # Assign the variable
  # Store the key and value in a variable with a : separator
  var=$(echo "$key:$value")
  # Add the variable to the variables array
  variables+=($var)
done

# Get the path to the static file
template_file="template-deploy-${selection}-endpoint.py"
new_file="deploy-${selection}-endpoint.py"

cp ./_template/$template_file ./script/$new_file


# Loop over the variables
for var in "${variables[@]}"
do
  # Split the variable into key and value
  key=$(echo $var | cut -d':' -f1)
  value=$(echo $var | cut -d':' -f2)

  sed -i "s~$key~$value~g" ./script/$new_file
done

# Ask the user if they want to deploy the new file
read -p "Do you want to deploy the endpoint? (y/N) " response

if [[ "$selection" = "sm-lmi" ]];then
    echo "Creating Model artifact for deploying SageMaker LMI Container"
    model_id=$(for pair in "${variables[@]}"; do echo $pair | grep -w "model_base_name" | cut -d ':' -f2; done)
    echo $model_id
    rm -f model.tar.gz
    rm -rf code_${model_id}_deepspeed/.ipynb_checkpoints
    tar czvf model.tar.gz -C code_${model_id}_deepspeed .
fi

# If the user says yes, deploy the new file
if [[ $response =~ ^[Yy]$ ]]; then
  echo "Deploying the endpoint..."
  pip install sagemaker boto3 --upgrade  --quiet
  res=$(python3 ./script/$new_file)
  echo "Endpoint.." $res
fi