# Adapted from OpenAI's Vision example 
import streamlit as st
import base64
import requests
from openai import OpenAI
from utils.ui import BasicChat


class AppVision(BasicChat):
  
  def __init__(self) -> None:
    self._init("Vision", "👀")
    self.llm = OpenAI(base_url="http://localhost:1556/v1", api_key="not-needed")

    # Ask the user for a path on the filesystem:
    # path = input("Enter a local filepath to an image: ")
  
  
  def main(self):
    self.chat()
    
  def ask(self, query):
    path = "../data/erreur.jpg"
    # Read the image and encode it to base64:
    self.base64_image = ""
    try:
      image = open(path.replace("'", ""), "rb").read()
      self.base64_image = base64.b64encode(image).decode("utf-8")
      self.comment(query)
    except:
      st.write("Couldn't read the image. Make sure the path is correct and the file exists.")
    
    
  def comment(self, query=""):
    completion = self.llm.chat.completions.create(
      model="local-model", # not used
      messages=[
        {
          "role": "system",
          "content": "Vous êtes un ingénieur construction qui analyse des images.",
        },
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Lister les non conformités sur cette image ?"},
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{self.base64_image}"
              },
            },
          ],
        }
      ],
      max_tokens=1000,
      stream=True
    )

    for chunk in completion:
      if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content
        
        
        
if __name__ == "__main__":
    app = AppVision()
    app.main()