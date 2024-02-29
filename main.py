import boto3
import json
import sys
from KBSearch import KBSearch


def main():
    # Set your BedRock KM ID
    kmID = 'your-km-id'
    # Set your BedRock FM ARN
    modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
    searcher = KBSearch(kmID, modelArn)
    #agentClient = boto3.client('bedrock-agent')
    print("----------------------------------------------------------\nInput : ")
    for line in sys.stdin:
        if 'q' == line.rstrip():
            break
        searchText = str(line)
        print ("LOADIND...", end="\r")
        #searchText = 'โทษครับของ พรบ อาคารชุด มีอะไรบ้าง'
        #searchText = 'บทลงโทษผู้ที่ฝ่าฝืนบทบัญญัติมีอะไรบ้าง'
        result =  searcher.RetrieveAndGenerate(searchText)
        resultText = result['output']['text']
        citations = result['citations']#
        for citation in citations:
            retrievedReferences = citation['retrievedReferences']
            for ref in retrievedReferences:
                print(ref['location']['s3Location']['uri'])
        print("Output : ")
        print(resultText)
        print("----------------------------------------------------------\nInput : ")
    print("Exit")
    
main()