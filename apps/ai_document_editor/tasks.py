from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
import openai
from dotenv import load_dotenv, find_dotenv
import os
from django.conf import settings

google_gemini = ChatGoogleGenerativeAI(model="gemini-pro",
                              tempreature = 0.5,
                              convert_system_message_to_human=True,
                              )


def define_memory(k=7):

    '''
    desc:

        define_memory() is a fuction can be used to instantiate the memory.
        We need the memory to store the previous conversation between the User and the AI
    '''

    '''
    Params and args:

        k [Optional=7]: k is the number of conversation chat history that are saved in the memory.
    '''

    '''
    return:

         This function returns Memory as Object.
    '''

    memory = ConversationBufferWindowMemory(k=k)

    return memory

memory = define_memory()

def define_conv_chain(memory, llm=google_gemini):


    '''
    desc:

        define_conv_chain() is a fuction can be used to instantiate the conversational chain.
        conversational chain used to connect between the LLM and the memory
    '''

    '''
    Params and args:

        memory [Required]: Memory to store chat history.
        llm [Optional=google_chat_palm]: The LLM.
    '''

    '''
    return:

         This function Conversation chain as object that can be used for conversation.
    '''

    conv_chain = ConversationChain(
        llm=llm,
        memory=memory
    )

    return conv_chain


conv_chain = define_conv_chain(memory)

def chat(conv_chain, message):


    '''
    desc:

        chat() is a fuction can be used to start conversation between user and AI.
    '''

    '''
    Params and args:

        conversation chain [Required]: A chain that connects between LLM and the memory
    '''

    '''
    return:

         dosen't return anything
    '''

    ans = conv_chain.predict(input=message)
    return ans
