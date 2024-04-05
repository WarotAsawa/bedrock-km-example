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
        
    def Retrieve(self, text, knowledgeID):
        response = self.agentRuntimeClient.retrieve(
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
    
    def RetrieveAndGenerate(self,text, modelArn, knowledgeID):
        response = self.agentRuntimeClient.retrieve_and_generate(
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
        return response
    
    def GetKMID(self):
        client = boto3.client('bedrock-agent')
        response = client.list_knowledge_bases()
        return response
      
    def ListAllKM(self):
        try:
            client = boto3.client('bedrock-agent', region_name="us-east-1")
            response = client.list_knowledge_bases()
            return response['knowledgeBaseSummaries']
        except Exception as e:
            print(f"Error retrieving List: {e}")
            return []
            
    def GetKMNameFromID(self, KMID):
        try:
            response = self.agentRuntimeClient.get_knowledge_base(knowledgeBaseId=KMID)
            return response['knowledgeBase']['name']
        except Exception as e:
            print(f"Error retrieving KM name from ID: {KMID}: {e}")
            return "Cannot find KM ID"

    def ListKMFMID(self):
        client = boto3.client('bedrock', region_name='us-east-1')
        response = client.list_foundation_models(byInferenceType='ON_DEMAND')
        return response['modelSummaries']

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
        self.agentRuntimeClient = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        self.translateClient = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        self.ssm_client = boto3.client('ssm', region_name='us-east-1')

        #agentClient = boto3.client('bedrock-agent')