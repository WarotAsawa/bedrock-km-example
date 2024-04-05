import streamlit as st #all streamlit commands will be available through the "st" alias
from KBSearch import KBSearch
st.set_page_config(page_title="Chatbot KM Demo") #HTML title

defaultKMID = 'R6D2NW0H7N'
modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1"
searcher = KBSearch()
kmList = searcher.ListAllKM();

# Streamlit BedRock LM List KM dropdowm
kmNameList = [];
for km in kmList:
    if (km['status'] == 'ACTIVE'):
        kmNameList.append(km['name'])
        

#selector col and headline col
headCol, selectCol = st.columns([0.7, 0.3])

with selectCol:
    kmOption = st.selectbox('Select your KM:' , kmNameList)
    
# Set KMID to match the selected KM Name
kmDes = "Chat bot with KM"
for km in kmList:
    if kmOption == km['name']:
        kmID = km['knowledgeBaseId']
        kmDes = str(km['description'])
        break;
    else:
        kmID = defaultKMID;
# Headline Streamlit
with headCol:
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
    kmName = ":gray[Now using KM :] *:green[" + kmOption +"]*"
    st.markdown(kmName)
    if modelArn != "":
        modelName = modelArn.split('/')[1]
        modelName = ":gray[Now using model :] *:orange[" + modelName +"]*"
        st.markdown(modelName)
    
if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history

for message in st.session_state.chat_history: #loop through the chat history
    with st.chat_message(message["role"]): #renders a chat line for the given role, containing everything in the with block
        if "help" in message: st.markdown(message["text"], help=message["help"]) #display the chat content
        else: st.markdown(message["text"]) #display the chat content


inputText = st.chat_input("Chat with your bot here") #display a chat input box
#searcher.Retrieve("text", kmID)
if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user"): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    thaiResponse = searcher.TranslateToThai(inputText)
    thaiInput = thaiResponse.get('TranslatedText')
    sourceLan = thaiResponse.get('SourceLanguageCode')
    print(sourceLan)
    modelResponse = searcher.RetrieveAndGenerate(thaiInput, modelArn, kmID)
    textResponse = modelResponse['output']['text']#call the model through the supporting library
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
    
    # Translate back
    chatResponse = searcher.TranslateFromThai(textResponse,sourceLan)
    
    with st.chat_message("assistant"): #display a bot chat message
        if sourceHelp == "":
            st.markdown(chatResponse) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history
        else:
            sourceHelp = "**Refered from :green["+str(sourceCount)+"] sources:**\n\n"+sourceHelp
            st.markdown(chatResponse, help=sourceHelp) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse, "help":sourceHelp}) #append the bot's latest message to the chat history


