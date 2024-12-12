#!/bin/sh

set -e

# this will create venv from python version defined in .python-version
if [ ! -d .venv ]; then
  uv venv
fi

# Activate the virtual environment using the dot command
. .venv/bin/activate

# install requirements for the project
uv pip install --upgrade -r requirements.txt --quiet

# run app using python from venv
echo "Running Netflix fetcher with $(python3 --version) at '$(which python3)'"


# Prompt the user for inputs
read -p "Enter your Netflix email: " NETFLIX_EMAIL
read -p "Enter your Netflix password: " NETFLIX_PASSWORD
read -p "Enter your Netflix profile: " NETFLIX_PROFILE

# Export the variables
export NETFLIX_EMAIL
export NETFLIX_PASSWORD
export NETFLIX_PROFILE

python3 main.py

# deactivate the virtual environment
deactivate
