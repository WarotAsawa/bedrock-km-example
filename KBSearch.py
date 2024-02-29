import boto3
import json
import sys

class KBSearch:
    def Retrieve(self,client, knowledgeID, text):
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
    
    def RetrieveAndGenerate(self,text):
        response = self.agentRuntimeClient.retrieve_and_generate(
            #sessionId='string',
            input={
                'text': text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': self.knowledgeID,
                    'modelArn': self.modelArn
                }
            }
            #,sessionConfiguration={
            #    'kmsKeyArn': 'string'
            #}
        )
        #print(response['retrievedReferences'])
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

    def __init__(self, knowledgeID, modelArn):

        self.knowledgeID = knowledgeID
        self.modelArn = modelArn
        self.agentRuntimeClient = boto3.client('bedrock-agent-runtime')
        self.translateClient = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        
        #agentClient = boto3.client('bedrock-agent')
    
        
