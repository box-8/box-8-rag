####
#### Streamlit Streaming using LM Studio as OpenAI Standin
#### run with `streamlit run app.py`

# !pip install pypdf langchain langchain_openai 

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from utils.ui import BasicChat


class AppChat(BasicChat):
    def __init__(self, title="CHAT Bot", icon="🤖"):
        self._init(title,icon)
        
    def main(self):
        # sidebar
        
        self.options()
        self.chat()  
        
    
        
if __name__ == "__main__":
    app = AppChat("Chatbot","🎶")
    app.main()