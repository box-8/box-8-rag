class Prompts():
    
    def basic(self):
        template = """  
        Répondre en français à la Question ci aprés en vous basant sur ce Contexte : {contexte}
        Question: {question}
        """
        
    def template2(self):
        template2="""
Using the following document text:
---------
{contexte}
---------
Present an answer to the following question as a JSON. There will always be two keys in the JSON. 
The first key is the "Reasoning" key that explicitly walks through the prompt step by step in order to provide the answer. 
The second key is the "Answer" key that only provides the final answer. For example, {{"Reasoning": "200 - 120 is 80", "Answer": "80"}}
If you cannot find an answer, please return an empty string for the "Answer" key. For example, {{"Reasoning": "It is not clear what the account number is", "Answer": ""}}
Answer an reason in the same language as the Question.

Question: 
{question}
"""
    def template3(self):
        prompts = """
Répondre en français à la Question ci aprés en vous basant sur ce contexte :{context}
Question :{question}
"""
prompts="""
répondre au format json selon le modèle {"annee":"en quelle année est apparut le reggae ?"}
"""
