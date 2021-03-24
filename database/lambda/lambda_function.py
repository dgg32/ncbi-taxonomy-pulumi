

import json
import functions

def lambda_handler(event, context):
    """
    This function fetches content from MySQL RDS instance
    """
    
    output = None
    
    if "resource" in event:
        method = event["resource"].replace("/", "")
    
        if "queryStringParameters" in event:
            if "taxid" in event["queryStringParameters"]:
                taxid = event["queryStringParameters"]["taxid"]

                if method == "getnamebytaxid":
                    output = functions.getNameByTaxid(taxid)
                
                elif method == "getrankbytaxid":
                    output = functions.getRankByTaxid(taxid)
                        
                elif method == "getparentbytaxid":
                    output = functions.getParentByTaxid(taxid)
                        
                elif method == "getdictpathbytaxid":
                    output = functions.getDictPathByTaxid(taxid)
                        
                elif method == "getsonsbytaxid":
                    output = functions.getSonsByTaxid(taxid)
        
            elif "name" in event["queryStringParameters"]:
                name = event["queryStringParameters"]["name"]

                if method == "gettaxidbyname":
                    output = functions.getTaxidByName(name)
                    
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(output),
        "isBase64Encoded": False
    }
    
    return response
    
