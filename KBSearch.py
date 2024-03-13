import boto3
import json
import sys
import mysql.connector
import re

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
            #sessionId='string',
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
    
    def GetSSMParameter(self, paramName):
        return self.get_ssm_parameter(paramName)
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
        self.runtimeClient = boto3.client('bedrock-runtime',region_name='us-east-1')
        self.translateClient = boto3.client(service_name='translate', region_name='us-east-1', use_ssl=True)
        self.ssm_client = boto3.client('ssm', region_name='us-east-1')

        #agentClient = boto3.client('bedrock-agent')
        
    # A function to query MySQL using sql statement
    def query(self, sql):
        # Connect to the database
        conn = mysql.connector.connect(
            host=self.get_ssm_parameter('kb-chat-demo-mysql-endpoint'),
            user=self.get_ssm_parameter('kb-chat-demo-mysql-username'),
            password=self.get_ssm_parameter('kb-chat-demo-mysql-string'),
            database=self.get_ssm_parameter('kb-chat-demo-mysql-databasename')
        )
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SQL statement
        try:
            cursor.execute(sql)
        except:
            return "ERROR"
        # Fetch the results
        results = cursor.fetchall()
        # Close the cursor and connection
        cursor.close()
        conn.close()
        # Return the results
        return results
    
    def BedrockPredict(self, prompt):
        inputJson = {
	        "messages": [{
			    "role":"user","content":[{
			        "type":"text",
					"text": prompt + "\\n"
				}]
		    }],
	        "anthropic_version":"bedrock-2023-05-31",
	        "max_tokens":4096,
	        "temperature":1,
	        "top_k":250,
	        "top_p":0.999,
	        "stop_sequences":["\\n\\nHuman:"]
        }
        inputData = json.dumps(inputJson)
        #print(inputData)
        modelId = "anthropic.claude-3-sonnet-20240229-v1:0"

        # Invoke the model for inference
        response = self.runtimeClient.invoke_model(contentType='application/json', body=inputData, modelId=modelId)

        # Retrieve the inference response
        result = response['body'].read().decode('utf-8')
        inferenceJson = json.loads(result) 
        # Process the inference result
        result = inferenceJson['content'][0]['text']
        return result;
        
    # A function to query MySQL using sql statement and return as JSON format 
    def queryJson(self, sql):
        # Connect to the database
        conn = mysql.connector.connect(
            host=self.get_ssm_parameter('kb-chat-demo-mysql-endpoint'),
            user=self.get_ssm_parameter('kb-chat-demo-mysql-username'),
            password=self.get_ssm_parameter('kb-chat-demo-mysql-string'),
            database=self.get_ssm_parameter('kb-chat-demo-mysql-databasename')
        )
        # Create a cursor object
        cursor = conn.cursor()
        # Execute the SQL statement
        try:
            cursor.execute(sql)
        except:
            return {}
        # Fetch the results
        rows = cursor.fetchall()
        # Close the cursor and connection
        result = []
        for row in rows:
            d = {}
            for i, col in enumerate(cursor.description):
                d[col[0]] = str(row[i])
            result.append(d)
        # Convert the list of dictionaries to JSON and print it
        #print(result)
        json_result = json.dumps(result)
        cursor.close()
        conn.close()
        # Return the results
        return json_result
        
    # Generate SQL Query prompt from questions 
    def GenerateSQLQueryPrompt(self, question):
        tables = self.query('SHOW TABLES;')
        allTableStatements = ""
        for table in tables:
            query = 'SHOW CREATE TABLE ' + table[0]
            #return as array with 1 objects and the object is tuple with (tablename, queryresult)
            showResult = self.query(query)[0][1]
            # Remove DB Engine, keep column and type only
            showResult = re.sub(r"ENGINE.*", "", showResult)
            #print (showResult)

            allTableStatements = allTableStatements + showResult + "\n\n"
        
        prompt = "Here is Here is my MySQL tables below:\n\n<mysql>\n"
        prompt = prompt + allTableStatements + "\n</mysql>\n\n\n"
        prompt = prompt + """Please convert the below statement into MySQL 8.0 Query. 
        If there are no limit apply, please input LIMIT 20 as default value. 
        Output in json format.
        JSON Key "query", ONLY OUTPUT SQL CODE ENCLOSED IN THREE BACKTICKS Inside a double quote.
        JSON Key "description" PROVIDE QUERY DETAIL DESCRIPTION AFTER IN JSON Key.\n\n<statement>\n"""
        prompt = prompt + question
        prompt = prompt + "\n</statement>"
        #print(prompt)
        return prompt
        
    # Generate SQL Statement from Prompt
    def PredictSQLQueryStatement(self, question):
        prompt = self.GenerateSQLQueryPrompt(question)
        sqlResult = self.BedrockPredict(prompt)
        sqlResult = re.sub(r".*SELECT", "SELECT", sqlResult)
        sqlResult = re.sub(r"```", "", sqlResult)
        sqlResult = re.sub(r'\"\"\"', '\"', sqlResult)
        sqlResult = re.sub(r"json", "", sqlResult)
        print(sqlResult)
        jsonResult = {}
        try:
            jsonResult = json.loads(sqlResult,strict=False);
        except:
            print("Json extract error")
            jsonResult = {}
            
        return jsonResult
    
    def GenerateAnswerFromQuestion(self, question):
        prompt = "Here is my query result data as below:\n<result>"
        generatedSQL = self.PredictSQLQueryStatement(question)
        result = {}
        # Chect generated SQL error
        if generatedSQL == {}:
            result['text'] = "Unexpected error occured when generate SQL Query, please try again."
            return result;
        sqlStatement = generatedSQL['query']
        print("Query JSON: " + sqlStatement)

        sqlStatement = re.sub(r'sql', '', sqlStatement)
        #Get QueryJson and check error
        queryJson = self.queryJson(sqlStatement)
        if queryJson == {}:
            result['text'] = "Unexpected error occured when query the database, please try again."
            return result;
        prompt = prompt + str(queryJson)
        #print(str(queryJson))
        prompt = prompt + "\n</result>\n"
        prompt = prompt + "\nPlease use the result to provide the answers from the question. Be truthful, short, concise and honest. Please do not provide introduction. Please provide the answers in friendly language."
        prompt = prompt + "\n<question>\n"
        prompt = prompt + question
        prompt = prompt + "\n</question>\n"
        result['text'] = self.BedrockPredict(prompt)
        result['query'] = generatedSQL
        return result;