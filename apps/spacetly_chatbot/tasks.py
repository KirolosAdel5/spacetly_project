from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.llms import GooglePalm
from langchain.chat_models import ChatGooglePalm
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from django.conf import settings
import os

google_api_key = settings.GOOGLE_API_KEY
openai_api_key = settings.OPENAI_API_KEY

def call_palm(google_api_key:str, temperature=0.5, max_tokens=8000, top_p=0.95, top_k=40, n_batch=9, repeat_penalty=1.1, n_ctx=8000):
    
    '''
    desc:
    
        call_palm() is a fuction can be used to instantiate a Google Palm model. 
        this model can be used to generate text, translate languages, write different kinds of creative content, and answer your questions in an informative way.
    '''
    
    '''
    Params and args:
    
        google_api_key (str): Required Parameter -> The Google API key for the Palm model.
        temperature (float): Optional Parameter -> The temperature parameter controls the randomness of the generated text. A higher temperature will result in more creative and varied text, but it may also be less accurate.
        max_output_tokens (int): Optional Parameter -> The maximum number of tokens to generate.
        top_p (float): Optional Parameter -> The top_p parameter controls the diversity of the generated text. A higher top_p will result in more diverse text, but it may also be less coherent.
        top_k (int): Optional Parameter -> The top_k parameter controls the number of tokens to consider when generating text. A higher top_k will result in more accurate text, but it may also be less creative.
        n_batch (int): Optional Parameter -> The n_batch parameter controls the number of batches to use when generating text. A higher n_batch will result in faster generation, but it may also be less accurate.
        repeat_penalty (float): Optional Parameter -> The repeat_penalty parameter controls the penalty for repeating tokens. A higher repeat_penalty will result in more diverse text, but it may also be less fluent.
        n_ctx (int): Optional Parameter -> The n_ctx parameter controls the context length used to generate text. A higher n_ctx will result in more coherent text, but it may also be slower to generate.
    '''
    
    '''
    return:
    
         This function returns Google Palm as language model object. 
         This object can be used to generate text, translate languages, write different kinds of creative content, and answer your questions in an informative way.
    '''
        
    google_palm_model = ChatGooglePalm(
        
         google_api_key=google_api_key,
         temperature=temperature,
         max_output_tokens=max_tokens,
         top_p=top_p,
         top_k=top_k, 
         n_batch=n_batch,
         repeat_penalty = repeat_penalty,
         n_ctx = n_ctx
    )
    
    return google_palm_model

google_chat_palm = call_palm(google_api_key)

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


def define_conv_chain(memory, llm=google_chat_palm):
    
     
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
        'Google PalM 2': google_chat_palm,
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

initial_conv_chain = define_conv_chain(memory, google_chat_palm)

def chat_logic(message_list, ai_model):
    # Your existing logic to initialize the conversation chain and interact with the chat model
    memory = define_memory()
    if ai_model == 'ChatGPT':
        chat_model = define_conv_chain(memory, chat_openai_gpt3)
    elif ai_model == 'GPT4':
        chat_model = define_conv_chain(memory, chat_openai_gpt4)
    elif ai_model == 'Google PalM 2':
        chat_model = define_conv_chain(memory, google_chat_palm)
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