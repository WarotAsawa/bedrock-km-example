import boto3
import json
import sys
from KBSearch import KBSearch
import time

# Fucntion to retrieve all model ID for BedRock at us-east-1

def main():
    kmID = 'ALFNIKHIEX'
    modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1"
    searcher = KBSearch(kmID)
  
    
    #modelList = searcher.ListKMID()
    #for model in modelList:
    #    print(model['modelArn'])
    #agentClient = boto3.client('bedrock-agent')
    print("----------------------------------------------------------\nInput : ")
    for line in sys.stdin:
        if 'q' == line.rstrip():
            break
        searchText = str(line)
        start_time = time.time()
        print ("LOADIND...", end="\r")
        #searchText = 'โทษครับของ พรบ อาคารชุด มีอะไรบ้าง'
        #searchText = 'บทลงโทษผู้ที่ฝ่าฝืนบทบัญญัติมีอะไรบ้าง'
        retrievedDict = searcher.Retrieve(searchText, kmID)
        print("Vector Search done in %s seconds" % (time.time() - start_time))
        start_time = time.time()
        print ("LOADIND...", end="\r")
        result =  searcher.RetrieveAndGenerate(searchText, modelArn, kmID)
        resultText = result['output']['text']
        '''
        citations = result['citations']#
        for citation in citations:
            retrievedReferences = citation['retrievedReferences']
            for ref in retrievedReferences:
                print(ref['location']['s3Location']['uri'])
        '''
        print("Output : ")
        print(resultText)
        print("Answers provided in %s seconds" % (time.time() - start_time))

        print("----------------------------------------------------------\nInput : ")
    print("Exit")
    #print(GetKMID(agentClient))
    
main()


