from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI

# Create an instance of ChatOpenAI with GPT-3.5
chat_openai_gpt3 = ChatOpenAI(temperature=0.5,)

def do_prompt(prompt):
    # Create PromptTemplate
    prompt_template = PromptTemplate(
        input_variables=["text_input"],
        template='You are content creator:\n{text_input}\n result: '
    )
    
    # Create LLMChain with GPT-3.5 and PromptTemplate
    chain = LLMChain(llm=chat_openai_gpt3, prompt=prompt_template)
    
    # Use invoke function instead of deprecated run function
    res = chain.invoke(prompt)

    return res

# prompt = """
# please Suggest_company_name with this info : 
# company_name:software 
# company_descraption:company provieded software solutions 
# Language: arabic
# Target Audience: men
# Number of Results: 10
# Tone of Voice: professional 

# make sure that the result be in markdown format
# """
# print(do_prompt(prompt))