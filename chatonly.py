import streamlit as st #all streamlit commands will be available through the "st" alias
from KBSearch import KBSearch
st.set_page_config(page_title="Chatbot KM Demo") #HTML title
st.markdown("""
<style>
.stProgress .st-bo {
    background-color: #479B86;
}
</style>
""", unsafe_allow_html=True)

defaultKMID = 'R6D2NW0H7N'
defaultPromptTemplate = """
You are a question answering agent named Nova. Please converse with the user using friendly words. Always answer with the same Language with the user.

"""
modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-instant-v1"

# Set Model Arn list for select option
modelArnList = [
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20240620-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-pro-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-lite-v1:0",
    "arn:aws:bedrock:us-east-1::foundation-model/amazon.nova-micro-v1:0"
];
# Gen Model Name from ARN
modelNameList = []
for model in modelArnList:
    modelNameList.append(model.split('/')[1])

#selector col and headline col
sideBar = st.sidebar
# Sidebar component
with sideBar:
    st.subheader('Model Selector 🧠:')
    llmOption = st.selectbox('Select your LLM for answer generation:' , modelNameList)
    
# Set modelArn
for model in modelArnList:
    modelName = model.split('/')[1]
    if modelName == llmOption: modelArn = model; break;

# set header
st.image('./img/bedrock.svg')
title = "BedRock Chat Demo"
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
- ช่วยเขียน คำโฆษณาของ Amazon Bedrock โดยใช้คำแบบ TikTok Influencer
- ช่วยเขียน คำโฆษณาของ Tranium และ Inferentia โดยใช้คำแบบโฆษณาหนัง
""")

#Streamlit Show ModelName 
with idCol:
    st.markdown(":gray[Now using model :] *:orange[" + llmOption +"]*"
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
            progressBar = st.progress(0)
            thaiResponse = searcher.TranslateToThai(inputText)
            progressBar.progress(33)
            thaiInput = thaiResponse.get('TranslatedText')
            sourceLan = thaiResponse.get('SourceLanguageCode')
            print(sourceLan)
            modelResponse = searcher.RetrieveAndGenerate(thaiInput, modelArn, kmID, numberOfResults, searchType, promptTemplate)
            progressBar.progress(66)
            textResponse = modelResponse['output']['text']#call the model through the supporting library
            # Translate back
            chatResponse = searcher.TranslateFromThai(textResponse,sourceLan)
            progressBar.progress(100)
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
        
            progressBar.empty()
            if sourceHelp == "":
                st.markdown(chatResponse) #display bot's latest response
                st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history
            else:
                sourceHelp = "**Refered from :green["+str(sourceCount)+"] sources:**\n\n"+sourceHelp
                st.markdown(chatResponse, help=sourceHelp) #display bot's latest response
                st.session_state.chat_history.append({"role":"assistant", "text":chatResponse, "help":sourceHelp}) #append the bot's latest message to the chat history
