#!/bin/bash

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
properties_file="./${selection}.properties"

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

cp $template_file $new_file


# Loop over the variables
for var in "${variables[@]}"
do
  # Split the variable into key and value
  key=$(echo $var | cut -d':' -f1)
  value=$(echo $var | cut -d':' -f2)

  sed -i "s~$key~$value~g" $new_file
done
