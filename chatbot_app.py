import streamlit as st #all streamlit commands will be available through the "st" alias
import logging
from KBSearch import KBSearch

st.set_page_config(page_title="Warot's KB Chatbot") #HTML title
st.title("Warot's KB Chatbot") #page title
st.text("See prompt example here:", help="Amazon BedRock คืออะไร , AWS public IPv4 address มีกี่ประเภท , EC2 มีกี่ Instance Type , AWS Certified Data Engineer มีค่าสอบเท่าไหร่, what is c6a instance type?, 什么是亚马逊 BedRock ?, Amazon BedRock là gì? Hãy trả lời bằng câu trả lời chi tiết")

kmParameterName = 'kb-chat-demo-km-id'
fmParameterName = 'kb-chat-demo-fm-arn'

searcher = KBSearch()
kmID = searcher.get_ssm_parameter(kmParameterName)
modelArn = searcher.get_ssm_parameter(fmParameterName)


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

searcher.Retrieve("text", kmID)
if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user"): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    kmID = str(searcher.get_ssm_parameter(kmParameterName))
    modelArn = searcher.get_ssm_parameter(fmParameterName)
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    thaiResponse = searcher.TranslateToThai(inputText)
    thaiInput = thaiResponse.get('TranslatedText')
    sourceLan = thaiResponse.get('SourceLanguageCode')
    logMessage = {}
    logMessage['kmID'] = kmID
    logMessage['modelArn'] = modelArn
    logMessage['sourceLanguage'] = sourceLan
    logMessage['inputText'] = inputText
    logging.warning(logMessage)
    modelResponse = searcher.RetrieveAndGenerate(thaiInput, kmID, modelArn) #call the model through the supporting library
    textResponse = modelResponse['output']['text']#call the model through the supporting library
    # Get all referenced source from the Citations
    sourceHelp = "Source 🗃️ : \n"
    allURL = ""
    citations = modelResponse['citations']#
    for citation in citations:
        retrievedReferences = citation['retrievedReferences']
        for ref in retrievedReferences:
            if allURL != "": allURL += " , "
            allURL += str(ref['location']['s3Location']['uri'])
    
    # Translate back
    chatResponse = searcher.TranslateFromThai(textResponse,sourceLan)
    with st.chat_message("assistant"): #display a bot chat message
        if allURL == "":
            st.markdown(chatResponse) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history
        else:
            sourceHelp = sourceHelp + allURL
            st.markdown(chatResponse, help=sourceHelp) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse, "help":sourceHelp}) #append the bot's latest message to the chat history
