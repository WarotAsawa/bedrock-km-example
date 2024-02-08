# BedRock Knowledge Chatbot
A Python app for BedRock KM demo with Amazon Translate.
The default language is Thai, but you can input any languages supported by Amazon Translate.
[Amazon Translate supported languages](https://docs.aws.amazon.com/translate/latest/dg/what-is-languages.html)

## Prerequisite
This code required Boto3 and Streamlit to run. To install, please run the cli below.
```
pip install boto3
pip install streamlit
```

## How to run?
Clone this repository into your local host.
```
git clone https://github.com/WarotAsawa/bedrock-km-example.git
```

Get into the folder.
```
cd bedrock-km-example
```

Edit the code , and run this command to run.
```
streamlit run chatbot_app.py --server.port 8080
```
