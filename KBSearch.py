import boto3
import json
import sys

class KBSearch:
    
    def get_ssm_parameter(self,parameter_name):
        try:
            response = self.ssm_client.get_parameter(Name=parameter_name)
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Error retrieving SSM parameter {parameter_name}: {e}")
            return None
        return None
        
    def Retrieve(self, text, kmID):
        response = self.agentRuntimeClient.retrieve(
            knowledgeBaseId=kmID,
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
    
    def RetrieveAndGenerate(self,text, kmID, modelArn):
        response = self.agentRuntimeClient.retrieve_and_generate(
            input={
                'text': text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': kmID,
                    'modelArn': modelArn
                }
            }
        )
        return response
    
    def GetKMID(self,client):
        response = client.list_knowledge_bases()
        return response
    
    def TranslateToThai(self, text):
        response = self.translateClient.translate_text(
            Text=str(text),
            SourceLanguageCode='auto',
            TargetLanguageCode='TH',
        )
        return response
    
    def TranslateFromThai(self, text, lan):
        response = self.translateClient.translate_text(
            Text=str(text),
            SourceLanguageCode='auto',
            TargetLanguageCode=lan
        )
        return response.get('TranslatedText')

    def __init__(self):
        self.agentRuntimeClient = boto3.client('bedrock-agent-runtime',region_name='us-east-1')
        self.translateClient = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        self.ssm_client = boto3.client('ssm', region_name='us-east-1')

