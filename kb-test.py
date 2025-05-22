import boto3
import json
import sys


def Retrieve(client, knowledgeID, text):
    response = client.retrieve(
        knowledgeBaseId=knowledgeID,
        retrievalQuery={
            'text': text
        },
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 10
            }
        }    
    )
    return response 

def RetrieveAndGenerate(client, knowledgeID, text, modelArn):
    response = client.retrieve_and_generate(
        #sessionId='string',
        input={
            'text': text
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledgeID,
                'modelArn': modelArn
            }
        }
        #,sessionConfiguration={
        #    'kmsKeyArn': 'string'
        #}
    )
    return response['output']['text']

def GetKMID(client):
    response = client.list_knowledge_bases()
    return response

    
def main():
    kmID = 'GOKJMUEK3E'
    modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
    agentRuntimeClient = boto3.client('bedrock-agent-runtime')
    #agentClient = boto3.client('bedrock-agent')

    print("----------------------------------------------------------\nInput : ")
    for line in sys.stdin:
    
        if 'q' == line.rstrip():
            break
        searchText = str(line)
        print ("LOADIND...", end="\r")
        #searchText = 'โทษครับของ พรบ อาคารชุด มีอะไรบ้าง'
        #searchText = 'บทลงโทษผู้ที่ฝ่าฝืนบทบัญญัติมีอะไรบ้าง'
        result =  RetrieveAndGenerate(agentRuntimeClient, kmID, searchText,modelArn)
        
        print("Output : ")
        print(result)
        print("----------------------------------------------------------\nInput : ")
    print("Exit")
    #print(GetKMID(agentClient))
    
main()