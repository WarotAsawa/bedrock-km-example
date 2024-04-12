import json
import boto3
import mysql.connector
import re 

class SQLSearch:
    def get_ssm_parameter(self,parameter_name):
        try:
            response = self.ssm_client.get_parameter(Name=parameter_name)
            return response['Parameter']['Value']
        except Exception as e:
            print(f"Error retrieving SSM parameter {parameter_name}: {e}")
            return None
        return None
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
    
    def BedrockPredict(self, prompt, temperature=0.9):
        inputJson = {
	        "messages": [{
			    "role":"user","content":[{
			        "type":"text",
					"text": prompt + "\\n"
				}]
		    }],
	        "anthropic_version":"bedrock-2023-05-31",
	        "max_tokens":4096,
	        "temperature":temperature,
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
        print(prompt)
        return prompt
        
    def GetSQLQueryStatement(self, sqlResult):
        sqlResult = re.sub(r".*SELECT", "SELECT", sqlResult)
        sqlResult = re.sub(r"```", "", sqlResult)
        sqlResult = re.sub(r'\"\"\"', '\"', sqlResult)
        sqlResult = re.sub(r"json", "", sqlResult)
        jsonResult = {}
        try:
            jsonResult = json.loads(sqlResult,strict=False);
        except:
            print("Json extract error")
            jsonResult = {}
        return(jsonResult)
        
    def __init__(self, region_name):
        self.region_name = region_name
        self.ssm_client = boto3.client('ssm', region_name=self.region_name)
        self.runtimeClient = boto3.client('bedrock-runtime', region_name=self.region_name)