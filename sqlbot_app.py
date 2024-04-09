import streamlit as st #all streamlit commands will be available through the "st" alias
import logging
from KBSearch import KBSearch
import re

searcher = KBSearch()


st.set_page_config(page_title="Amazon Bedrock SQL Chatbot", page_icon=":brain:") #HTML title
st.image('./img/bedrock.svg')
st.title("Amazon Bedrock SQL Chatbot") #page title
st.markdown("See prompt example here:  ", help="""- Which department Shin Birdsall is in? 
- Top 20 employee with biggest salary and their salary.
- List each Department name and its total number of employee.
- list top 10 manager with highest number of employee.
- What are average salary of each job title, ranking from highest to lowest in table format.
""")
with open('db-schema.sql', 'r') as file:
    data = file.read()
st.markdown(":gray[Now using database:] :green[employees]", 
help="Database Schema: \n ```sql\n"+data+"\n```")

modelArn = "anthropic.claude-3-sonnet-20240229-v1:0"
if modelArn != "":
    #modelName = modelArn.split('/')[1]
    modelName = ":gray[Now using model :] *:orange[" + modelArn +"]*"
    st.markdown(modelName)
    
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

if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user", avatar='./img/human.svg'): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    logMessage = {}
    #logMessage['kmID'] = kmID
    #logMessage['modelArn'] = modelArn
    #logMessage['sourceLanguage'] = sourceLan
    #logMessage['inputText'] = inputText
    #logging.warning(logMessage)
    modelResponse = searcher.GenerateAnswerFromQuestion(inputText) #call the model through the supporting library
    chatResponse = modelResponse['text']#call the model through the supporting library
    # Get all referenced source from the Citations
    if 'query' in modelResponse:
        queryTooltip = modelResponse['query']['query']
        descriptionTooltip = modelResponse['query']['description']
        descriptionTooltip = re.sub(r"'", "`", descriptionTooltip)
        # addd sql source tag
        sourceHelp = "Query : \n```sql" + queryTooltip + "```\n\n" + descriptionTooltip
    else:
        sourceHelp = "ERROR"
    # Translate back
    with st.chat_message("assistant",avatar='./img/bedrock-avatar.svg'): #display a bot chat message
        if sourceHelp == "ERROR":
            st.markdown(chatResponse) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history
        else:
            st.markdown(chatResponse, help=sourceHelp) #display bot's latest response
            st.session_state.chat_history.append({"role":"assistant", "text":chatResponse, "help":sourceHelp}) #append the bot's latest message to the chat history
