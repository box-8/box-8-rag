import os
import streamlit as st
import chromadb
import pandas as pd
from chromadb.config import Settings

from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from langchain_community.document_loaders.pdf import PyMuPDFLoader 

from utils.models import AppModels
from utils.embeddings import DATA_PATH, EMBEDDINGS
from utils.ui import AppRag


class AppHome(AppRag):
    
    def main(self) :
        
        collections = self.client.list_collections()  # obtenir la liste des collections
        if not collections:  # vérifier si la liste des collections est vide
            st.write("Il n'y a pas de collections.")
            self.create_collection("langchain")
        
        super().sidebar()
        
        collection_selectionnee = self.client.get_collection(self.collectionName)
                
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Collection", "Documents", "Fichiers", "Models", "Options"])
        with tab1:
            st.header(f"Collection {self.collectionName}")
            new_collection_name = st.text_input(label="Nom de la collection",placeholder="Nom de la collection", value=self.collectionName)
        
            colc1, colc2, colc3 = st.columns(3)
            with colc1 :
                if st.button("⚠️ Supprimer la collection", key="delete_collection") :
                    self.delete_collection(self.collectionName)
                    st.rerun()
            with colc2 :
                    
                if st.button("💸 Nouvelle collection ...", key="collection_create"): 
                    if new_collection_name == self.collectionName:
                        "le nom exites déja"
                    else:
                        collection_selectionnee = self.create_collection(name=new_collection_name)    
                        st.rerun() 
                
                
            with colc3:
                if st.button("💸 Rename collection ...", key="collection_rename"): 
                    "rename collection"
                    collection_selectionnee = self.rename_collection(name=new_collection_name)    
                    st.rerun() 
                # self.ui_actions(collection_selectionnee)
            self.visualiser(collection_selectionnee)
            
            
        with tab2:
            st.header(f"Collection {self.collectionName} : documents")
            colf1, colf2= st.columns(2)
            with colf1:
                uploaded_doc = st.file_uploader("🚩 Ajouter un document dans " + self.collectionName, type=["pdf", "txt", "docx", "jpg"])
                if uploaded_doc is not None:
                    saved_path = self.save_uploaded_doc(uploaded_doc)
                    if st.button("Vectoriser le doc"):
                        self.vectoriser(file_path=saved_path, collectionName=self.collectionName)
            with colf2:
                docs_in_collection = self.list_documents(collectionName=self.collectionName)
                nom_document_supprimer = st.selectbox("Choisissez le document à supprimer de la collection", docs_in_collection)
                if st.button("⚠️ Supprimer un document",key="delete_document_confirm"):
                    self.delete_document(collectionName=self.collectionName, documentName=nom_document_supprimer)
        
        with tab3:
            # Liste des fichiers du répertoire "data"
            st.header(f"Fichiers sur le disque")
            data_files = os.listdir(DATA_PATH)
            data_files = [file for file in data_files if file.endswith(('.pdf', '.txt', '.docx', '.jpg'))]

            # Afficher la liste des fichiers dans la sidebar
            selected_file = st.selectbox("Choisissez un document parmi les fichiers :", data_files)

            # Charger et afficher l'image sélectionnée depuis le répertoire "images"
            if selected_file:
                selected_data_path = os.path.join(DATA_PATH, selected_file)
                if selected_file.endswith('.jpg'):
                    st.image(selected_data_path, caption=selected_file, use_column_width=True)
            
            col1, col2, col3 = st.columns(3)

            with col1:
                button1 = st.button('Effacer')

            with col2:
                button2 = st.button('Ouvrir')

            with col3:
                button3 = st.button('Vectoriser')
                
            if button1:
                if selected_file:
                    os.remove(selected_data_path)
                    st.sidebar.success(f"Le document {selected_file} a été supprimée avec succès.")
            if button2:
                if selected_file:
                    os.startfile(selected_data_path)
            if button3:
                if selected_file:
                    self.vectoriser(file_path=selected_data_path, collectionName=self.collectionName)
        with tab4:
            models = AppModels()
            models.main()
        with tab5: 
            st.header("Options")
            self.container_options = st.container()
            super().options(self.container_options)
            
        
        
    
    def ui_actions(self,collection_selectionnee):
        options_menu = ["Choisir une action","Ajouter un élément", "Mettre à jour un élément", "Supprimer un élément"]
        option_selectionnee = st.selectbox("Choisissez une action", options_menu)

        if option_selectionnee == "Ajouter un élément":
            nouvelle_embedding = st.text_input("Entrez l'embedding du nouvel élément :")
            nouveau_metadata = st.text_input("Entrez les métadonnées du nouvel élément :")
            nouvel_id = st.text_input("Entrez l'ID du nouvel élément :")

            # Ajouter le nouvel élément à la collection
            if st.button("Ajouter l'élément"):
                collection_selectionnee.add(embeddings=[float(nouvelle_embedding)],
                                metadatas={"meta": nouveau_metadata},
                                ids=nouvel_id)
                st.write(f"L'élément {nouvel_id} a été ajouté.")

        elif option_selectionnee == "Mettre à jour un élément":
            # Mettre à jour un élément existant dans la collection
            id_element_a_mettre_a_jour = st.text_input("Entrez l'ID de l'élément à mettre à jour :")
            embedding_mis_a_jour = st.text_input("Entrez l'embedding mis à jour de l'élément :")
            metadata_mis_a_jour = st.text_input("Entrez les métadonnées mises à jour de l'élément :")
            if st.button("Mettre à jour l'élément"):
                collection_selectionnee.update(ids=id_element_a_mettre_a_jour,
                                    embeddings=[float(embedding_mis_a_jour)],
                                    metadatas={"meta": metadata_mis_a_jour})
                st.write(f"L'élément {id_element_a_mettre_a_jour} a été mis à jour.")

        elif option_selectionnee == "Supprimer un élément":
            # Supprimer un élément de la collection
            id_element_a_supprimer = st.text_input("Entrez l'ID de l'élément à supprimer :")
            if st.button("Supprimer l'élément"):
                collection_selectionnee.delete(ids=id_element_a_supprimer)
                st.write(f"L'élément {id_element_a_supprimer} a été supprimé.")

    def save_uploaded_doc(self, uploaded_file):
        # Sauvegarder l'image téléchargée sur le disque
        file_name = uploaded_file.name.lower()
        
        with open(os.path.join(DATA_PATH, file_name), "wb") as f:
            f.write(uploaded_file.getbuffer())
        return os.path.join(DATA_PATH, file_name)

        
    def visualiser(self,collection):
        df = pd.DataFrame.from_dict(collection.get())
        st.dataframe(df, width=1400)
        return df 
        # Sélectionner une ligne en cliquant sur un index dans la colonne 'ids'
        
        selected_id = st.selectbox('Sélectionner une ligne', df['ids'])

        # Afficher les attributs de la ligne sélectionnée
        if selected_id is not None:
            selected_row = df[df['ids'] == selected_id].iloc[0]
            st.write('Attributs de la ligne sélectionnée :')
            for index, value in selected_row.items():
                st.write(f"{index}: {value}")
                
    def vectoriser(self, file_path, collectionName="langchain"):
        loader = PyMuPDFLoader(file_path=file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            #add_start_index=True,
        )
        chunks = text_splitter.split_documents(documents)
        """
        Vectorisation en cours
        """
        self.chroma_db.add_documents(documents=chunks)
        st.success(f"Le document a été vectorisé avec succès à l'emplacement : {file_path}")
        st.balloons()




    def delete_document(collectionName, documentName, client):
        collection = client.get_or_create_collection(name=collectionName)
        df = pd.DataFrame.from_dict(collection.get())
        filtered_ids = set()
        for index, row in df.iterrows():
            metadatas = row['metadatas']
            if documentName in metadatas["file_path"]:
                filtered_ids.add(row['ids'])
        
        chroma_db = Chroma(
            client=client,
            collection_name=collectionName,
            embedding_function=EMBEDDINGS(),
        )
        for document_id in filtered_ids:
            chroma_db.delete(document_id)

        # Persist the changes
        # chroma_db.persist()

        return collection

    def create_collection(self,name):
        collection = self.client.get_or_create_collection(name=name)
        self.init_collections()
        # st.session_state.collection = self.noms_collections[0]
        "collection created"
        return collection
    
    def rename_collection(self, name):
        if name =="":
            return
        else :
            collection = self.client.get_or_create_collection(name=st.session_state.collection)
            collection.modify(name)
        
    def delete_collection(self,name):
        collection = self.client.delete_collection(name=name)
        self.init_collections()
        "collection supprimée"
        return collection
    
    
if __name__ == "__main__":
    app = AppHome("VectorDB","🏝️")
    app.main()