import streamlit as st
import os
import socket
import requests
import subprocess
import psutil
import llama_cpp

from utils.embeddings import * 
from utils.session import BasicSession

script_directory = os.path.abspath(os.path.dirname(__file__))
# Chemin absolu vers le répertoire "models"
models_directory = os.path.abspath(os.path.join(script_directory, "..", "models")).replace("\\", "/")
# Chemin absolu vers le répertoire de l'environnement virtuel (.venv/Scripts/activate.bat)
venv_directory = os.path.abspath(os.path.join(models_directory, "..", ".venv", "Scripts", "activate.bat")).replace("\\", "/")



class AppModels(BasicSession):
    def __init__(self) -> None:
        self.session_init()
    
    
    def cached_llm(self):
        CACHED_LLM = []
        files = self.list_models()
        if not files:
            st.write("Aucun fichier trouvé dans le répertoire 'models'")
        else:
            for file in files:
                port_number = self.generate_port_number(file)
                if st.session_state.llm_port == port_number:
                    is_active = True
                else : 
                    is_active = False
                if self.is_service_running(port_number):
                    is_running = True
                else:
                    is_running = False
                entry = {"name":os.path.basename(file), "port": port_number, "is_running": is_running, "is_active":is_active}
                CACHED_LLM.append(entry)
        return CACHED_LLM
    
    def models_dropdown(self,container=None):
        options = list()
        cachedllms = self.cached_llm()
        idex = 0 
        for index, models in enumerate(cachedllms):
            name = models["name"]
            port_number = models["port"]
            if str(st.session_state.llm_port) == str(port_number):
                idex = index
            if models["is_running"] :
                prefix = "👍"  
            else:
                prefix = "👎"
                
            if models["is_active"] :
                prefix1 = "✔️" 
            else:
                prefix1 = " "
            
            entry = f"{prefix} {prefix1} : {name} :{port_number}"
            options.append(entry)
        
        if not container : 
            selected_entry = st.selectbox("llm model", options=options, index=idex)
        else : 
            selected_entry = container.selectbox("llm model", options=options, index=idex)
        if selected_entry:
            parts = selected_entry.split(':')
            selected_port = int(parts[-1].strip())
            selected_file = parts[-2].strip()
            model_path = os.path.join(models_directory, selected_file)
            st.session_state.llm_port = selected_port
            if not self.is_service_running(selected_port) :
                self.start_service(model_path=model_path,port=selected_port)
                
    def is_service_running(self,port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    
    def list_models(self):
        files = os.listdir(models_directory)
        return [f for f in files if os.path.isfile(os.path.join(models_directory, f))]

    def stop_service(self, port):
        for proc in psutil.process_iter(['pid', 'connections']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        proc.terminate()
                        return proc
            except psutil.NoSuchProcess:
                # Ignore les processus qui n'existent plus
                pass
        return "Not Stopped"


            
    def generate_port_number(self,file_name):
        # Convertir le nom de fichier en une valeur numérique en utilisant la somme des codes ASCII des caractères
        file_value = sum(ord(char) for char in file_name)
        # Utiliser le modulo pour obtenir un numéro de port entre 1500 et 1600
        port_number = 1500 + (file_value % 101)  # 101 est un nombre premier pour une distribution plus uniforme
        return port_number


    def start_service(self,model_path, port):
        
        # Commande à exécuter
        command = ["python", "-m", "llama_cpp.server", "--model", model_path, "--port", str(port)]

        # Exécute la commande en activant d'abord l'environnement virtuel
        # process = subprocess.Popen([venv_directory, "&&"] + command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # Exécute la commande en activant d'abord l'environnement virtuel et en redirigeant les E/S
        process = subprocess.Popen([venv_directory, "&&"] + command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        # Attendre que le processus se ter mine et récupérer la sortie
        return True


    def button_start(self, container, file, port_number):
        model_path = os.path.join(models_directory, file)
        start_button = container.button(f"Démarrer le modèle sur {port_number}", key=file)
        if start_button:
            self.start_service(model_path, port_number)
            self.set_service(file, port_number)
            self.button_stop(container,port_number)    

    def button_stop(self, container,port_number):
        test_stoped= container.button(f"Arrêter le modèle sur {port_number}", on_click=self.stop_service, args=(port_number,))
        if not test_stoped :
            pass
        elif test_stoped =="Not Stopped":
            st.error(f"Server could not be stopped {port_number}")
        else:
            st.write(test_stoped) 
            st.success(f"Server stopped {port_number}")

    def set_service(self, modelname, port):
        st.session_state.llm_modelname = modelname
        st.session_state.llm_port = port
    
            
    def main(self):
        st.markdown("## Gestion des modèles 🍀")
        
        CACHED_LLM = []
        files = self.list_models()
        if not files:
            st.write("Aucun fichier trouvé dans le répertoire 'models'")
        else:
            
            line = st.empty()
            col1, col2, col3 = line.columns(3)
            
            with col1 :
                if st.session_state.llm_port == "groq":
                    btype = "primary"
                else:
                    btype = "secondary"
                button_groq = st.button(f"Mistral 8x7b on GROQ", type=btype, key=f"port_groq", on_click=self.set_service, args=("groq mistral","groq",))
            with col2 :
                button_groq2 = st.button(f"Démarrer le modèle sur Groq", type="secondary", key=f"port_groq2", on_click=self.set_service, args=("groq mistral","groq",))
                
            for file in files:
                port_number = self.generate_port_number(file)
                with col1:
                    if st.session_state.llm_port == port_number:
                        btype = "primary"
                        is_active = True
                    else : 
                        btype = "secondary"
                        is_active = False
                    
                    button_set = st.button(f"{file}", type=btype, key=f"port_{port_number}", on_click=self.set_service, args=(file,port_number,))
                        
                with col2:
                    container = st.empty()
                    
                    if self.is_service_running(port_number):
                        self.button_stop(container, port_number)
                        is_running = False
                    else:
                        self.button_start(container, file, port_number)
                        is_running = True
                entry = {"name":file, "port": port_number, "is_running": is_running, "is_active":is_active}
                
                CACHED_LLM.append(entry)
                
                
                
if __name__ == "__main__":
    App = AppModels()
    App.main()
