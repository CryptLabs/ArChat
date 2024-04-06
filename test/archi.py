import os
print(os.getcwd())

import sys
import argparse
import yaml
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import GPT4All

from langchain import hub
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# from pyfiglet import Figlet
# from termcolor import colored

# f = Figlet(font='slant')

# print(colored(f.renderText('ArchI'), 'green'))

# # Adding a subtitle
# #f = Figlet(font='standard')
# print(colored('Your Terminal Friendly Arch Linux AI Assistant!\n','yellow'))
# print(colored("Loading ...\n", 'green'))

def parse_args(config: dict, args: list):
    """Parses command line arguments.

    Args:
        config (dict): items in config.yaml
        args (list(str)): user input parameters

    Returns:
        dict: dictionary of items in config.yaml, modified by user input parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-embed", dest="test_embed", action="store_true")
    args = parser.parse_args(args)
    if args.test_embed:
        config["Arch_Linux_Data_Sources"] = ["archwiki"]
        config["data_dir"] = "./test_data"
        config["question"] = "What is the the best editor for the terminal in Arch Linux?"

    return config

def load_config():
    """Loads configuration from config.yaml file.

    Returns:
        dict: items in config.yaml
    """
    try:
        with open("./config.yaml", "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except FileNotFoundError:
        print("Error: File config.yaml not found.")
        sys.exit(1)
    except yaml.YAMLError as err:
        print(f"Error reading YAML file: {err}")
        sys.exit(1)

    return data

config = load_config()

#print(config['Arch_Linux_Data_Sources'])

## Use chromadb to get the data 

# query it
#query = "where is the consolefonts foler located in Arch Linux?"


# Load an LLM
def load_llm(llm_type):
    if llm_type == "ChatOpenAI":
        llm = ChatOpenAI(temperature=0.5, openai_api_key="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")
    elif llm_type == "GPT4All":
        llm = GPT4All(
            model=r"/home/al1nux/Projects/models/orca-mini-3b-gguf2-q4_0.gguf",
            max_tokens=2048,
        )
    else:
        raise ValueError("Invalid LLM type")
    return llm

# Print the result
#print(res["output_text"])

def greet_user():
    print(colored("Hello, I'm ArchI! How can I assist you today?\n", 'cyan'))

def get_user_query():
    return input(colored("\nEnter your prompt (or 'quit' to exit):\n", 'cyan'))


def create_chat_prompt(query):
    template = (
        "You are a helpful Arch Linux assistant that answers {question} by finding answers from {input_documents}."
    )
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
   
    human_message_prompt = HumanMessagePromptTemplate.from_template(query)
    
    chat_prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
    )
    return chat_prompt

def search_knowledge_base(query):
    
    embeddings = HuggingFaceEmbeddings(
            cache_folder="./model",
            model_name=config["embeddings_model"],
            show_progress=False,
    )
    
    vectordb = Chroma(persist_directory=config["data_dir"],
                    embedding_function=embeddings)
    
    docs = vectordb.similarity_search(query)
    #print(colored("\nSearching knowledge base ...\n\n", 'red'))
    return docs

def get_answer(llm, chat_prompt, query):
    chain = load_qa_chain(llm, chain_type="stuff")
    res = chain.invoke({"prompt": chat_prompt, "input_documents": search_knowledge_base(query), "question": query})
#    print(res["output_text"], end='\n\n')
    return res["output_text"]
# def main():
#     greet_user()
#     print("Select the LLM model:\n")
#     print("1. ChatOpenAI (Online) (Fast), more acurate.")
#     print("2. GPT4All (Local) (Slow).")
#     llm_choice = input(colored("\nEnter the number corresponding to the LLM type: ", 'cyan'))
#     if llm_choice == '1':
#         llm_type = "ChatOpenAI"
#     elif llm_choice == '2':
#         llm_type = "GPT4All"
#     else:
#         print("\nInvalid choice. Exiting...")
#         return
#     llm = load_llm(llm_type)
#     while True:
#         query = get_user_query()
#         if query.lower() == 'quit':
#             break
#         chat_prompt = create_chat_prompt(query)
#         get_answer(llm, chat_prompt, query)
#     print("\nEnjoy your day!")

# main()



########################################33333

#print(docs[0].page_content)


# # quantize and Run your LLM locally
# llm = GPT4All(
#     model=r"/home/al1nux/Projects/models/orca-mini-3b-gguf2-q4_0.gguf",
#     max_tokens=2048,
# )

# result = llm.invoke("explain Retrieval Augmented Generation?")

#print(result)

# retriever = vectordb.as_retriever()
# rag_prompt = hub.pull("rlm/rag-prompt")
# docs = retriever.get_relevant_documents("LUKS2")

# Create the langchain with retriever,
# prompt template and LLM
# qa_chain = (
#     {"context": retriever | from_documents, "question": RunnablePassthrough()}
#     | rag_prompt
#     | llm
#     | StrOutputParser()
# )



# print(qa_chain.invoke("what is LUKS2?"))