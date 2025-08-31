import os
from typing import List, Dict
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI

class QAAgent:
    def __init__(self, mode: str = "default"):
        self.llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7 if mode == "creative" else 0.1
        )
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Chroma(
            persist_directory="./chroma_db", 
            embedding_function=self.embeddings
        )
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        self.mode = mode
        self.setup_prompts()

    def setup_prompts(self):
        if self.mode == "interview":
            self.prompt_template = """
                You are Samukelo Mkhize’s Personal Codex Agent.
                Answer questions truthfully based only on the documents provided.
                Speak in Samukelo’s authentic voice: professional, reflective, concise but human.

                If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
                If the question is not about Samukelo, politely inform them that you are only able
                to answer questions about Samukelo based on the provided documents.

                {context}

                Question: {question}
                Answer in a concise and human manner.
                Answer:"""
        
        elif self.mode == "storytelling":
            self.prompt_template = """You are telling a story based on the following information.
                Weave the facts into an engaging narrative.

                {context}

                Question: {question}
                Answer:
            """

        else:  # default
            self.prompt_template = """You are a helpful assistant.
                Use the following pieces of context to answer the question at the end.
                If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.

                {context}

                Question: {question}
                Answer:"""
            
        self.QA_PROMPT = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )

    def get_qa_chain(self):
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )

        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            combine_docs_chain_kwargs={"prompt": self.QA_PROMPT}
        )

        return qa_chain
    
    def ask_question(self, question: str) -> str:
        qa_chain = self.get_qa_chain()
        result = qa_chain({"question": question})
        return result['answer']
    
    def clear_memory(self):
        self.memory.clear()