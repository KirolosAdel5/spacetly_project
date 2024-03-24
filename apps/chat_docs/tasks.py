from pprint import pprint 
from langchain import PromptTemplate 
from langchain.chains.question_answering import load_qa_chain 
from langchain.document_loaders import PyPDFLoader 
from langchain.text_splitter import RecursiveCharacterTextSplitter 
from langchain.vectorstores import Chroma 
from langchain.chains import RetrievalQA 
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
# from .utils import to_markdown
import os

class LangchainGemeni:

    def __init__(self, GOOGLE_API_KEY: str, temperature: float) -> None:
        self.GOOGLE_API_KEY = GOOGLE_API_KEY
        self.client = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY, temperature=temperature, convert_system_message_to_human=True)
        self.vector_index = None  # Initialize vector_index attribute

    def GenerateContent(self, prompt: str) -> str:
        response = self.client.invoke(prompt)
        return response

    def AIEmbeddingsPdfPages2Vector(self, pdf: str) -> object:
        pdf_loader = PyPDFLoader(pdf)
        pages = pdf_loader.load_and_split()
        self.pdf_pages = pages
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        context = "\n\n".join(str(p.page_content) for p in self.pdf_pages)
        texts = text_splitter.split_text(context)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=self.GOOGLE_API_KEY)
        self.vector_index = Chroma.from_texts(texts, embeddings).as_retriever()
        return self.vector_index

    def BuildQA(self, return_source_documents=True) -> object:
        if self.vector_index is None:
            raise ValueError("Vector index is not initialized. Please call AIEmbeddingsPdfPages2Vector method first.")
        qa_chain = RetrievalQA.from_chain_type(self.client, retriever=self.vector_index, return_source_documents=return_source_documents)
        return qa_chain

    
# model = LangchainGemeni(os.getenv("GOOGLE_API_KEY"), temperature=0.3)

# model.AIEmbeddingsPdfPages2Vector(r"D:\codeing and projects\spacetly_project\media\chat-ai-documents\Eyad_Aiman.pdf")

# # Summon your trusty Question-Answering guardian
# qa_client = model.BuildQA(return_source_documents=True)

# qa_model = qa_client({
#     'query': "can give me overview of context ? ",
# })

# print(qa_model['result'])

# views.py
# import os
# import requests
# from django.shortcuts import render
# from django.http import JsonResponse
# from PyPDF2 import PdfReader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# import google.generativeai as genai
# from langchain.vectorstores import FAISS
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.chains.question_answering import load_qa_chain
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_pdf_text(pdf_docs):
#     text = ""
#     for pdf in pdf_docs:
#         pdf_reader = PdfReader(pdf)
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#     return text


# def get_text_chunks(text):
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=10000, chunk_overlap=1000)
#     chunks = splitter.split_text(text)
#     return chunks

# def get_vector_store(chunks):
#     embeddings = GoogleGenerativeAIEmbeddings(
#         model="models/embedding-001")
#     vector_store = FAISS.from_texts(chunks, embedding=embeddings)
#     vector_store.save_local("/dja faiss_index")

# def get_conversational_chain():
#     prompt_template = """
#     Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
#     provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
#     Context:\n {context}?\n
#     Question: \n{question}\n

#     Answer:
#     """

#     model = ChatGoogleGenerativeAI(model="gemini-pro",
#                                    client=genai,
#                                    temperature=0.3,
#                                    )
#     prompt = PromptTemplate(template=prompt_template,
#                             input_variables=["context", "question"])
#     chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
#     return chain

# def clear_chat_history():
#     # Logic for clearing chat history
#     pass

# def user_input(user_question):
#     embeddings = GoogleGenerativeAIEmbeddings(
#         model="models/embedding-001")

#     # Load the FAISS index with dangerous deserialization allowed
#     new_db = FAISS.load_local("/django/public/faiss_index", embeddings, allow_dangerous_deserialization=True)
#     docs = new_db.similarity_search(user_question)

#     chain = get_conversational_chain()

#     response = chain(
#         {"input_documents": docs, "question": user_question}, return_only_outputs=True)

#     return response



