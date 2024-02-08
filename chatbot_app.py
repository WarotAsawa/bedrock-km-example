import streamlit as st #all streamlit commands will be available through the "st" alias
from KBSearch import KBSearch

st.set_page_config(page_title="Warot Chatbot") #HTML title
st.title("Warot Chatbot") #page title
# Select your BedRock KM ID
kmID = 'your-km-id'
# Select your BedRock FM ARN
modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
searcher = KBSearch(kmID, modelArn)

if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history



for message in st.session_state.chat_history: #loop through the chat history
    with st.chat_message(message["role"]): #renders a chat line for the given role, containing everything in the with block
        st.markdown(message["text"]) #display the chat content


inputText = st.chat_input("Chat with your bot here") #display a chat input box

if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user"): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    thaiResponse = searcher.TranslateToThai(inputText)
    thaiInput = thaiResponse.get('TranslatedText')
    sourceLan = thaiResponse.get('SourceLanguageCode')
    print(sourceLan)
    modelResponse = searcher.RetrieveAndGenerate(thaiInput) #call the model through the supporting library
    chatResponse = searcher.TranslateFromThai(modelResponse,sourceLan)
    with st.chat_message("assistant"): #display a bot chat message
        st.markdown(chatResponse) #display bot's latest response
    
    st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history


