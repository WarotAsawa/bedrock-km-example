# BedRock Knowledge Chatbot
A Python app for BedRock KM demo with Amazon Translate.
The default language is Thai, but you can input any languages supported by Amazon Translate.
[Amazon Translate supported languages](https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html)

## Prerequisite

Clone this repository into your local host.
```
git clone https://github.com/WarotAsawa/bedrock-km-example.git
```
Get into the folder.
```
cd bedrock-km-example
```
This code required Boto3 and Streamlit to run. To install, please run the cli below.
```
pip install -r ./requirements.txt
```
Please make sure your application are using IAM User or Role with permission below.
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "translate:TranslateText"
                "ssm:Describe*",
                "ssm:Get*",
                "ssm:List*"
                "s3:Get*",
                "s3:List*",
                "s3:Describe*",
                "bedrock:GetFoundationModel",
                "bedrock:ListFoundationModels",
                "bedrock:RetrieveAndGenerate",
                "bedrock:InvokeModel",
                "bedrock:Retrieve",
                "bedrock:ListKnowledgeBases",
                "bedrock:GetKnowledgeBase",
                "bedrock:ListDataSources",
                "bedrock:GetDataSource"
            ],
            "Resource": ["<your resources scope>"]
        }
    ]
}
```
## How to run?

Get into the folder.
```
cd bedrock-km-example
```

Edit the code , and run this command to run.
```
streamlit run chatbot_app.py --server.port 8080
```
Then access the web app with your browser with http://localhost:8080