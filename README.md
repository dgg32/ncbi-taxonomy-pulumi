
  

  

# Introduction

  

  

This repository contains code and data for my article "".

1. The graphql_genbank folder contains three GBK files and scripts for importing and querying. They were used in the tutorial

  

2. The other scripts are pulumi setup file.

  

  
# Introduction

This repo contains code for the NCBI taxonomy Rest Api in my article Five Commands Build Two NCBI APIs on the Cloud via Pulumi.

# Prerequisite

  

Pulumi ([https://www.pulumi.com/docs/get-started/](https://www.pulumi.com/docs/get-started/))


# Usage
1. you need to unzip "data_files.zip" in the "database" folder. They are the NCBI taxonomy data in two tables.
  
2. initialize pulumi python, make sure you have cd into "database" folder, and issue
```console
pulumi new aws-python
```
3. set up Aurora
```console
pulumi up -y
```
4. import the data
```console
python zip_and_import.py $(pulumi stack output instance-endpoint)
```
5. set up Lambda and Api Gateway. Make sure you have cd into "lambda_api_gateway" folder. Issue:
```console
pulumi up -y
```
6. To tear down the infrastruture, issue:
```console
pulumi destroy -y
```
  

## Authors

  

*  **Sixing Huang** - *Concept and Coding*

  

## License

  

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
