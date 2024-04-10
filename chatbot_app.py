import streamlit as st #all streamlit commands will be available through the "st" alias
from KBSearch import KBSearch
st.set_page_config(page_title="Chatbot KM Demo") #HTML title

defaultKMID = 'R6D2NW0H7N'
if 'previouskmID' not in st.session_state: st.session_state['previouskmID'] = ""
modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1"
searcher = KBSearch('us-east-1')
kmList = searcher.ListAllKM();

# Streamlit BedRock LM List KM dropdowm
kmNameList = [];
for km in kmList:
    if (km['status'] == 'ACTIVE'):
        kmNameList.append(km['name'])
# Set Model Arn list for select option
modelArnList = [
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2:1",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"
];
# Gen Model Name from ARN
modelNameList = []
for model in modelArnList:
    modelNameList.append(model.split('/')[1])

#selector col and headline col
sideBar = st.sidebar
kmSelector = st.sidebar
# Sidebar component
with sideBar:
    st.subheader('BedRock KMs Selector')
    kmOption = st.selectbox('Select your KM 📄:' , kmNameList)
    st.subheader('KM LLM Selector 🧠:')
    llmOption = st.selectbox('Select your LLM for answer generation:' , modelNameList)
    st.subheader('KM Source File Tree 🌳:')
    dirContainer = st.container(height=500, border=False)
# Set modelArn
for model in modelArnList:
    modelName = model.split('/')[1]
    if modelName == llmOption: modelArn = model; break;
# Set KMID to match the selected KM Name
kmDes = "Chat bot with KM"
for km in kmList:
    if kmOption == km['name']:
        kmID = km['knowledgeBaseId']
        kmDes = str(km['description'])
        break;
    else:
        kmID = defaultKMID;
# If the selection is same KMID, do not Get S3 again
if 'sourceFiles' not in st.session_state: st.session_state['sourceFiles'] = searcher.S3TreeFromKM(kmID)
if st.session_state['previouskmID'] != kmID:
    #print(st.session_state['previouskmID'], kmID)
    st.session_state['sourceFiles'] = searcher.S3TreeFromKM(kmID)
    st.session_state['previouskmID'] = kmID
    #print(st.session_state['previouskmID'], kmID)
sourceFiles = st.session_state['sourceFiles']

with dirContainer:
    bucketExpanderList = []
    for sourceFile in sourceFiles:
        bucketExpander = st.expander("📗 "+sourceFile['bucket'])
        bucketExpanderList.append(bucketExpander)
        with bucketExpander:
            allText = ""
            if 'root' in sourceFile:
                for rootFile in sourceFile['root']:
                    allText = allText +"  \n├  📄 " + rootFile
            for key in sourceFile:
                if key == 'root': continue
                if key == 'bucket': continue
                allText = allText +"  \n├  📁 " + key
                for rootFile in sourceFile[key]:
                    allText = allText +"  \n  ├  📄 " + rootFile
            st.markdown(allText)
# set header
st.image('./img/bedrock.svg')
title = kmDes + " Demo"
st.title(title) #page title

#hint col and model KM col
hintCol, idCol = st.columns(2)
with hintCol:
    st.markdown("See prompt example here:  ", help="""
- Amazon BedRock คืออะไร
- AWS public IPv4 address มีกี่ประเภท
- EC2 มีกี่ Instance Type
- AWS Certified Data Engineer มีค่าสอบเท่าไหร่
- what is c6a instance type?
- 什么是亚马逊 BedRock ?
- Amazon BedRock là gì? Hãy trả lời bằng câu trả lời chi tiết
""")

#Streamlit Show ModelName 
with idCol:
    st.markdown(":gray[Now using KM :] *:green[" + kmOption +"]*  \n:gray[Now using model :] *:orange[" + llmOption +"]*"
                )
# Chatbox history
    
if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history

for message in st.session_state.chat_history: #loop through the chat history
    avatarImg = './img/human.svg'
    if message["role"] == "assistant": avatarImg = './img/bedrock-avatar.svg'
    newChatMessage = st.chat_message(message["role"], avatar=avatarImg);
    with newChatMessage: #renders a chat line for the given role, containing everything in the with block
        if "help" in message: st.markdown(message["text"], help=message["help"]) #display the chat content
        else: st.markdown(message["text"]) #display the chat content


inputText = st.chat_input("Chat with your bot here") #display a chat input box
#searcher.Retrieve("text", kmID)
if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user", avatar='./img/human.svg'): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    with st.chat_message("assistant",avatar='./img/bedrock-avatar.svg'): #display a bot chat message
        with st.spinner(" Thinking 🤔 ... "):
            thaiResponse = searcher.TranslateToThai(inputText)
            thaiInput = thaiResponse.get('TranslatedText')
            sourceLan = thaiResponse.get('SourceLanguageCode')
            print(sourceLan)
            modelResponse = searcher.RetrieveAndGenerate(thaiInput, modelArn, kmID)
            textResponse = modelResponse['output']['text']#call the model through the supporting library
            # Translate back
            chatResponse = searcher.TranslateFromThai(textResponse,sourceLan)
    
            # Get all referenced source from the Citations
            sourceHelp = ""
            sourceCount = 0
            citations = modelResponse['citations']#
            for citation in citations:
                retrievedReferences = citation['retrievedReferences']
                for ref in retrievedReferences:
                    sourceCount = sourceCount + 1;
                    sourceHelp += "Source " + str(sourceCount) + " 🗃️ : \n"
                    sourceHelp += "["+str(ref['location']['s3Location']['uri'])+"]("+str(ref['location']['s3Location']['uri'])+")\n\n"
                    sourceHelp += "Refered text:\n```\n"
                    sourceHelp += str(ref['content']['text']) + "\n"
                    sourceHelp += "```\n\n"
        
        
            if sourceHelp == "":
                st.markdown(chatResponse) #display bot's latest response
                st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history
            else:
                sourceHelp = "**Refered from :green["+str(sourceCount)+"] sources:**\n\n"+sourceHelp
                st.markdown(chatResponse, help=sourceHelp) #display bot's latest response
                st.session_state.chat_history.append({"role":"assistant", "text":chatResponse, "help":sourceHelp}) #append the bot's latest message to the chat history
