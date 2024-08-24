#!/bin/bash

# Se placer dans le répertoire approprié
cd /c/_prod/localgpt

# Lancer le serveur llama_cpp
python -m llama_cpp.server --model models/mistral-7b-instruct-v0.2.Q4_K_S.gguf --port 1234 &

# Attendre quelques secondes pour que le serveur se lance
sleep 5

# Lancer Streamlit
streamlit run home.py &

# Attendre quelques secondes pour que Streamlit se lance
sleep 5

# Lancer Chroma
chroma run --path ./chroma &

pause