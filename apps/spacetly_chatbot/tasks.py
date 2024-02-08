from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI

from dotenv import load_dotenv, find_dotenv
import os
from django.conf import settings


google_api_key = settings.GOOGLE_API_KEY
openai_api_key = settings.OPENAI_API_KEY


google_gemini = ChatGoogleGenerativeAI(model="gemini-pro",
                              tempreature = 0.5,
                              convert_system_message_to_human=True,
                              google_api_key=google_api_key
                              )

chat_openai_gpt3 = ChatOpenAI(temperature=0.5)
chat_openai_gpt4 = ChatOpenAI(temperature=0.5, model='gpt-4')

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

def define_conv_chain(memory, llm):
    conv_chain = ConversationChain(
        llm=llm,
        memory=memory
    )
    return conv_chain

def chat(conv_chain, aimodel, message):
    available_models = {
        'Google PalM 2': google_gemini,
        'ChatGPT': chat_openai_gpt3,
        'GPT4': chat_openai_gpt4,
    }

    model_name = aimodel

    if model_name not in available_models:
        print(f'Model {model_name} not available. Available models: {list(available_models.keys())}')
        return None

    model = available_models[model_name]
    memory = define_memory()
    conv_chain = define_conv_chain(memory, llm=model)

    message = message
    response = None
    ans = conv_chain.predict(input=message)
    response = ans
    return response

initial_conv_chain = define_conv_chain(memory, google_gemini)

def chat_logic(message_list, ai_model):
    # Your existing logic to initialize the conversation chain and interact with the chat model
    memory = define_memory()
    if ai_model == 'ChatGPT':
        chat_model = define_conv_chain(memory, chat_openai_gpt3)
    elif ai_model == 'GPT4':
        chat_model = define_conv_chain(memory, chat_openai_gpt4)
    elif ai_model == 'Google PalM 2':
        chat_model = define_conv_chain(memory, google_gemini)
    else:
        # Default to ChatGPT if the provided AI model is invalid
        chat_model = define_conv_chain(memory, chat_openai_gpt3)
    
    # Get the last message from the user
    last_user_message = message_list[-1]["content"]
    
    try:
        # Use the conversation chain to generate a response
        response = chat(chat_model, ai_model, last_user_message)
    except Exception as e:
        # Handle the case where an error occurs during response generation
        print(f"Error: {str(e)}")
        # Fallback to another model or provide a default response
        response = "I'm sorry, I couldn't generate a response at the moment. Please try again later."
    
    return response

def generate_title_request(message_list):
    try:
        openai.api_key = settings.OPENAI_API_KEY

        gpt3_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                         {"role": "system",
                          "content": "Summarize and make a very short meaningful title under 24 characters"},
                     ] + message_list
        )
        response = gpt3_response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        return "Problematic title with error."
    return response
