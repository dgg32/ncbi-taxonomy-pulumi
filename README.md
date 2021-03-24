
  
# Introduction

This repo contains code for the NCBI taxonomy Rest Api in my article Five Commands Build Two NCBI APIs on the Cloud via Pulumi.

# Prerequisite

  

Pulumi ([https://www.pulumi.com/docs/get-started/](https://www.pulumi.com/docs/get-started/))


# Usage
1. you need to unzip "data_files.zip" in the "database" folder. They are the NCBI taxonomy data in two tables.

2. Fill in all the details in rds_config.py

3. initialize pulumi python, make sure you have cd into "database" folder, and issue
```console
python -m virtualenv venv
source ./venv/Scripts/activate
pip install -r requirements.txt
```

4. set up Aurora
```console
pulumi up -y
```
5. import the data
```console
python zip_and_import.py $(pulumi stack output instance-endpoint)
```
6. set up Lambda and Api Gateway. Make sure you have cd into "lambda_api_gateway" folder. Issue:

```console
deactivate
python -m virtualenv venv
source ./venv/Scripts/activate
pip install -r requirements.txt

pulumi up -y
```
7. To tear down the infrastruture, issue:
```console
pulumi destroy -y
```
  

## Authors

  

*  **Sixing Huang** - *Concept and Coding*

  

## License

  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
