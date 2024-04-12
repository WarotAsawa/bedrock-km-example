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
    
    def RetrieveAndGenerate(self,text, modelArn, knowledgeID, numberOfResults, searchType, promptTemplate):
        response = self.agentRuntimeClient.retrieve_and_generate(
            input={
                'text': text
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledgeID,
                    'modelArn': modelArn,
                    'generationConfiguration': {
                        'promptTemplate': {
                            'textPromptTemplate': promptTemplate
                        }
                    },
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': numberOfResults,
                            'overrideSearchType': searchType
                        }
                    }
                }
            }
        )
        return response
    
    def GetKMID(self):
        client = boto3.client('bedrock-agent')
        response = client.list_knowledge_bases()
        return response
      
    def ListAllKM(self):
        try:
            client = boto3.client('bedrock-agent', region_name=self.region_name)
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
        client = boto3.client('bedrock', region_name=self.region_name)
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
    def ListS3AllPath(self, bucket, prefixList):
        client = boto3.client('s3')
        results = {}
        if len(prefixList) == 0:
            #result = client.list_objects(Bucket=bucket, Delimiter='/')
            paginator = client.get_paginator('list_objects')
            page_iterator = paginator.paginate(Bucket=bucket)
            for page in page_iterator:
                    for obj in page['Contents']:
                        if '/' in obj['Key']:
                            splitPath = obj['Key'].split('/',1)
                            if str(splitPath[0]) not in results:
                                results[str(splitPath[0])] = []
                            results[str(splitPath[0])].append(str(splitPath[1]))
                        else:
                            if 'root' not in results:
                                results['root'] = []
                            results['root'].append(obj['Key'])
        else:
            for prefix in prefixList:
                paginator = client.get_paginator('list_objects')
                page_iterator = paginator.paginate(Bucket=bucket,Prefix=prefix)
                for page in page_iterator:
                    for obj in page['Contents']:
                        if '/' in obj['Key']:
                            splitPath = obj['Key'].split('/',1)
                            if str(splitPath[0]) not in results:
                                results[str(splitPath[0])] = []
                            results[str(splitPath[0])].append(str(splitPath[1]))
                        else:
                            if 'root' not in results:
                                results['root'] = []
                            results['root'].append(obj['Key'])
        results['bucket']=bucket
        #print(results)
        return results

    def S3TreeFromKM(self, kmID):
        agentClient = boto3.client('bedrock-agent', region_name=self.region_name)
        datasource = agentClient.list_data_sources(knowledgeBaseId=kmID)
        datasourceList = datasource['dataSourceSummaries']
        bucketPrefixList = []
        results = []
        for datasource in datasourceList:
            sourceDetail = agentClient.get_data_source(dataSourceId=datasource['dataSourceId'],knowledgeBaseId=kmID)
            if (sourceDetail['dataSource']['dataSourceConfiguration']['type'] == 'S3'):
                bucketConfig = sourceDetail['dataSource']['dataSourceConfiguration']['s3Configuration']
                bucketPrefixList.append(bucketConfig)
                #bucketArn = sourceDetail['dataSource']['dataSourceConfiguration']['s3Configuration']['bucketArn']
                #prefixList = sourceDetail['dataSource']['dataSourceConfiguration']['s3Configuration']['inclusionPrefixes']

        #print(bucketPrefixList)
        for bucketPrefix in bucketPrefixList:
            prefix = []
            if 'inclusionPrefixes' in bucketPrefix:
                prefix = bucketPrefix['inclusionPrefixes']
            bucketName = bucketConfig['bucketArn'].split(':')[5]
            results.append(self.ListS3AllPath(bucketName, prefix))
        print("Updated bucket directory")
        return results

    def __init__(self, region_name):
        self.region_name = region_name
        self.agentRuntimeClient = boto3.client('bedrock-agent-runtime', region_name=self.region_name)
        self.translateClient = boto3.client(service_name='translate', region_name=self.region_name, use_ssl=True)
        self.ssm_client = boto3.client('ssm', region_name=self.region_name)

        #agentClient = boto3.client('bedrock-agent')