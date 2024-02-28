import streamlit as st #all streamlit commands will be available through the "st" alias
from KBSearch import KBSearch

st.set_page_config(page_title="Warot's KB Chatbot") #HTML title
st.title("Warot's KB Chatbot") #page title
st.text("See prompt example here:", help="Amazon BedRock คืออะไร , AWS public IPv4 address มีกี่ประเภท , EC2 มีกี่ Instance Type , AWS Certified Data Engineer มีค่าสอบเท่าไหร่")

parameterName = 'kb-chat-demo-km-id'
modelArn = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2"
searcher = KBSearch(modelArn)

if 'chat_history' not in st.session_state: #see if the chat history hasn't been created yet
    st.session_state.chat_history = [] #initialize the chat history

for message in st.session_state.chat_history: #loop through the chat history
    with st.chat_message(message["role"]): #renders a chat line for the given role, containing everything in the with block
        st.markdown(message["text"]) #display the chat content


inputText = st.chat_input("Chat with your bot here") #display a chat input box
kmID = searcher.get_ssm_parameter('kb-chat-demo-km-id')
searcher.Retrieve("text", kmID)
if inputText: #run the code in this if block after the user submits a chat message
    
    with st.chat_message("user"): #display a user chat message
        st.markdown(inputText) #renders the user's latest message
    kmID = str(searcher.get_ssm_parameter('kb-chat-demo-km-id'))
    print("Now using KM",kmID)
    st.session_state.chat_history.append({"role":"user", "text":inputText}) #append the user's latest message to the chat history
    thaiResponse = searcher.TranslateToThai(inputText)
    thaiInput = thaiResponse.get('TranslatedText')
    sourceLan = thaiResponse.get('SourceLanguageCode')
    print(sourceLan)
    modelResponse = searcher.RetrieveAndGenerate(thaiInput, kmID) #call the model through the supporting library
    chatResponse = searcher.TranslateFromThai(modelResponse,sourceLan)
    with st.chat_message("assistant"): #display a bot chat message
        st.markdown(chatResponse) #display bot's latest response
    
    st.session_state.chat_history.append({"role":"assistant", "text":chatResponse}) #append the bot's latest message to the chat history


