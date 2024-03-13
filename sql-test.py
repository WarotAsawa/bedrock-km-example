import boto3
import json
import sys
import time

from KBSearch import KBSearch


def main():
    #modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
    searcher = KBSearch()
    kmID = searcher.get_ssm_parameter('kb-chat-demo-km-id')
    print("----------------------------------------------------------\nInput : ")
    for line in sys.stdin:
        if 'q' == line.rstrip():
            break
        searchText = str(line)
        start_time = time.time()
        print ("LOADIND...", end="\r")
        result = searcher.GenerateAnswerFromQuestion(searchText)

        print("Output : ")
        print(result['text'])
        print("Answers provided in %s seconds" % (time.time() - start_time))

        print("----------------------------------------------------------\nInput : ")
    print("Exit")

main()