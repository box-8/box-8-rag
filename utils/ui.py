import streamlit as st
import time
import chromadb
import pandas as pd
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.vectorstores.chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

from utils.embeddings import EMBEDDINGS
from utils.session import BasicSession
from utils.llm import BasicLLM
from utils.models import AppModels

class BasicChat(BasicSession, BasicLLM):
    def _init(self, title="", icon=""):
        self.session_init()
        self.title = title
        self.icon = icon
        st.set_page_config(page_title=self.title, page_icon=self.icon, layout='wide')
        st.title(self.title + " "+ self.icon)
        
        self.llmLocal(st.session_state.llm_port) 
        
    def ui_context(self):
        opt_system_context = self.container_options.text_area("Contexte du Système :",key="opt_system_context", value=st.session_state.opt_system_context)
        if opt_system_context:
            self.setContext(context=opt_system_context)
        
    def setContext(self, context):
        newcontext = SystemMessage(content=context)
        st.session_state.history[0] = newcontext
        return newcontext
            
    def getDebug(self, text=""):
        if text =="":
            phrase = """Victor Hugo était un poète, romancier et dramaturge français, né le 26 février 1802 et décédé le 22 mai 1885. Il est considéré comme l'un des plus grands écrivains français de tous les temps. Ses œuvres les plus célèbres comprennent "Les Misérables" et "Les Contes du temps passé". Hugo a été également un député et sénateur de la République française, ainsi qu'un partisan actif des idées républicaines"""
        else : 
            phrase = text
            # a@todo v1.2
            # AppModels().models_dropdown()
        mots = phrase.split()
        for mot in mots:
            yield mot + " "
            time.sleep(0.1)
    
    def ui_k(self):
        opt_kfragments = self.container_options.slider('Retrieved fragments', value=st.session_state.opt_kfragments, min_value=2,max_value=6)
        if opt_kfragments:
            st.session_state.opt_kfragments = opt_kfragments
    
    def ui_debug(self):
        opt_debug = self.container_options.toggle('Debug mode', key="opt_debug_selector", value=st.session_state.opt_debug)
        st.session_state.opt_debug = opt_debug
            
    def options(self,container=None):
        # Si l'utilisateur choisit d'afficher le texte, afficher le text_area
        if not container:
            self.container_options = st.popover("options")
        
        if st.session_state.llm_modelname =="": 
            warn = "Choisir un modèle"
            st.page_link("home.py",label=warn)
            self.container_options.warning("Aucun modèle n'est sélectionné, rendez-vous sur la page home/modèles")
        else:
            self.container_options.info(f"{st.session_state.llm_modelname}")
        
        self.ui_context()
        col1, col2 = self.container_options.columns(2)
        with col1:
            self.ui_debug()
                
            if st.button("show session"):
                self.session_show()
            
        with col2:
            if self.container_options.button("Effacer chat"):
                self.history_reset()
            if st.button("kill session"):
                self.session_kill()
            self.ui_k()
        
        # @todo V1.2 
        # AppModels().models_dropdown(self.container_options)
        
    def chat(self):
        # conversation
        for message in st.session_state.history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)

        # user input
        user_query = st.chat_input("Type your message here...")
        if user_query is not None and user_query != "":
            st.session_state.history.append(HumanMessage(content=user_query))
            with st.chat_message("Human"):
                st.markdown(user_query)
            with st.chat_message("AI"):
                try:
                    response = st.write_stream(self.ask(user_query))
                except:
                    response = st.write_stream(self.getDebug("error connection to llm server"))
            st.session_state.history.append(AIMessage(content=response))

    def ask(self, query):
        if st.session_state.opt_debug :
            return self.getDebug()
        else:
            return self.get_response(query)
        
        
    def get_response(self, query):
        chatactual = st.session_state.history
        prompt = ChatPromptTemplate.from_messages(chatactual)
        chain = prompt | self.llm | StrOutputParser()
        return chain.stream({})

class AppRag(BasicChat):
    def __init__(self, title="RAG Bot", icon="🤖"):
        self._init(title,icon)
        
        self.client = chromadb.HttpClient(host='localhost', port=8000)
        self.init_collections()
        
    def init_collections(self):
        self.collections = self.client.list_collections()  # obtenir la liste des collections
        self.noms_collections = [col.name for col in self.collections] # obtenir les noms des collections
        self.collectionName = self.noms_collections[0]
        
    
    def sidebar(self):
        # sidebar
        if not self.collections:  # vérifier si la liste des collections est vide
            st.write("Il n'y a pas de collections.")
            return
        
        self.session_register("collection", self.noms_collections[0])
        
        if st.session_state.collection in self.noms_collections:
            default_idx_collection = self.noms_collections.index(st.session_state.collection)
        else:
            default_idx_collection = 0
        self.collectionName = st.sidebar.selectbox("Choisissez une collection", self.noms_collections, key="collection_selector", index=default_idx_collection)
        self.setCollection(self.collectionName)
        
        self.docs_in_collection = self.list_documents(collectionName = self.collectionName)
        # defaults = self.documents_communs()
        
        self.selected_docs = st.sidebar.multiselect("Choisissez les documents de la collection", self.docs_in_collection, key="selected_docs", default=st.session_state.selected_docs)
    
    def documents_communs(self, tab1, tab2):
        set1 = set(tab1)
        set2 = set(tab2)
        return list(set1.intersection(set2))
    
    def main(self):
        self.options()
        self.sidebar()
        st.write(st.session_state.opt_system_context)
        self.chat()
    
    def list_documents(self, collectionName):
        if collectionName == "Nouvelle collection ...":
            documents = []
        else:
            collection = self.client.get_or_create_collection(name=collectionName)
            df = pd.DataFrame.from_dict(collection.get())
            # Initialisation de la liste des documents unique
            documents = set()
            for index, row in df.iterrows():
                metadatas = row['metadatas']
                documents.add(metadatas["file_path"])
        return documents

    def setCollection(self, name=""):
        if name == "Nouvelle collection ...":
            self.collectionName = name
            st.session_state.collection = name
        else:
            self.collectionName = name
            st.session_state.collection = name
            self.chroma_db = Chroma(
                client=self.client,
                collection_name = self.collectionName,
                embedding_function=EMBEDDINGS(),
            )
    
    def get_response(self, query):
        kelements = st.session_state.opt_kfragments
        st.toast('Gathering information ...', icon='🎉')
        time.sleep(0.5)
        if not self.selected_docs:
            results = self.chroma_db.similarity_search_with_score(query, k=kelements)
        else:
            where = {
                "file_path": {
                    "$in": self.selected_docs
                }
            }
            results = self.chroma_db.similarity_search_with_score(query, filter=where, k=kelements)
        sorted_results = sorted(results, key=lambda x: x[1], reverse=True) 
        context = ""
        for doc, _score in sorted_results:
            context += f"{doc.page_content}"
            page_text = doc.page_content
            pct = str(round(_score, 2))
            mots = page_text.split()
            sumup = " ".join(mots[:100])
            time.sleep(0.5)
            st.toast(f"{pct} % \n"+ sumup, icon = "🍃")
            
           
        template="""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the Question.
    Question: {question} 
    ------
    Context: 
    {context}  
    ------
    If you don't know the answer, just say that you don't know. 
    Keep the answer concise and always ask the user a relevant question at the end of your reply
    """
        RAGMessage = HumanMessagePromptTemplate.from_template(template)
        chatactual = st.session_state.history.copy() # on crée une copie du chat 
        chatactual.pop() # on retire la question posée par l'utilisateur
        chatactual.append(RAGMessage) # on la remplace par celle calculée RAG
        
        prompt = ChatPromptTemplate.from_messages(chatactual)
        
        chain = prompt | self.llm | StrOutputParser()
        return chain.stream({
            "context": context,
            "question": query,
        })
    


    