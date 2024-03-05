import boto3
import json
import sys
from KBSearch import KBSearch


def main():
    modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
    searcher = KBSearch(modelArn)
    kmID = searcher.get_ssm_parameter('kb-chat-demo-km-id')

    print("----------------------------------------------------------\nInput : ")
    for line in sys.stdin:
        if 'q' == line.rstrip():
            break
        searchText = str(line)
        print ("LOADING...", end="\r")
        result =  searcher.RetrieveAndGenerate(searchText, kmID)
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