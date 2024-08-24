import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
# 1536

class BasicLLM():
    def llmLocal(self, port=1234) -> None:
        
        if port =="groq":
            self.base_url= "groq"
            self.api_key=st.secrets["GROQ_API_KEY"]
            self.llm = ChatGroq(temperature=0, groq_api_key=self.api_key, model_name="mixtral-8x7b-32768")
        else : 
    
            self.base_url= f"http://localhost:{port}/v1"
            self.api_key="no_key"
            self.llmSet(self.base_url, self.api_key)
    
    def llmBaseUrl(self, base_url):
        self.base_url = base_url
    
    def llmApikey(self, api_key):
        self.api_key = api_key
        
    def llmSet(self , base_url, api_key):
        self.llmBaseUrl(base_url)
        self.llmApikey(api_key)
        self.llm = ChatOpenAI(base_url=base_url,api_key=api_key)
        return self.llm
