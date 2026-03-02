import streamlit as st
import ollama
import os

st.set_page_config(page_title="PC Doc - Cyber Sec Assistant")

with st.sidebar:
    st.title('PC Doc - Cyber Sec Assistant')
    st.write('This chatbot is connected to the local Ollama model.')
    st.success('Ollama model is configured!', icon='✅')
    st.subheader('Models and parameters')
    selected_model = st.selectbox('Choose a model', ['Llama3-7B', 'Mistral-7B'], key='selected_model')
    print(selected_model)
    models={"Llama3-7B":'llama3',"Mistral-7B":"mistral"}    
    embedmodel = "nomic-embed-text"
    mainmodel = models[selected_model]
    print(embedmodel,mainmodel)


if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

import chromadb
chroma = chromadb.PersistentClient(path="./chromadb")
collection = chroma.get_or_create_collection("buildragwithpython")

def generate_llama2_response(prompt_input):    
    queryembed = ollama.embeddings(model=embedmodel, prompt=prompt_input)['embedding']
    relevantdocs = collection.query(query_embeddings=[queryembed], n_results=5)["documents"][0]
    docs = "\n\n".join(relevantdocs)

    modelquery = f"""
     Important instructions:
    1. Carefully read and analyze *all parts* of the context to ensure you fully understand the situation before making a decision.
    2. Focus on identifying *one primary attack type* based on the context and query.
    3. Only mention multiple attacks if the context *clearly shows evidence* of more than one attack. Otherwise, *focus solely on one attack*.
    4. If the query or context is *not related to cybersecurity*, respond with: "The query is not related to a cybersecurity issue, and I cannot provide an answer." and stop the chat, otherwise follow the below.

    You are a cybersecurity assistant. Based only on the following context, carefully read and analyze each part 
    of the context before determining which *single* type of cyber attack the user might be facing based on their query.

    

    ---

    Given the above context, what type of cyber attack may have occurred based on the problem described in the query: '{prompt_input}'?

   
    After identifying the attack:
    1. Provide a brief description of the attack and explain how it typically operates.
    2. Describe the potential effects or impact this attack has on the victim.
    3. Finally, suggest practical solutions or mitigation steps to resolve or prevent the attack.
    """

    
    response = ""
    stream = ollama.generate(model=mainmodel, prompt=modelquery, stream=True)
    for chunk in stream:
        if chunk["response"]:
            response += chunk['response']

    return response


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            placeholder.markdown(response)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
