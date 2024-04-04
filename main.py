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

from pyfiglet import Figlet
from termcolor import colored

f = Figlet(font='slant')

print(colored(f.renderText('ArchI'), 'green'))

# Adding a subtitle
#f = Figlet(font='standard')
print(" Version 0.1\n")
print(colored('Your Terminal Friendly Arch Linux AI Assistant!'))



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

embeddings = HuggingFaceEmbeddings(
        cache_folder="./model",
        model_name=config["embeddings_model"],
        show_progress=True,
)
# load from disk
vectordb = Chroma(persist_directory=config["data_dir"],
                  embedding_function=embeddings)

# query it
#query = "where is the consolefonts foler located in Arch Linux?"


# Load an LLM
#llm = ChatOpenAI(temperature=0, openai_api_key="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")
llm = GPT4All(
     model=r"/home/al1nux/Projects/models/orca-mini-3b-gguf2-q4_0.gguf",
     max_tokens=2048,
)

# Create the chain
chain = load_qa_chain(llm, chain_type="stuff")
#res = chain.invoke({"input_documents": docs, "question": query})

# Print the result
#print(res["output_text"])

while True:
    user_input = input("Enter your prompt (or 'quit' to exit):\n")
    if user_input.lower() == 'quit':
        break
    query = user_input
    docs = vectordb.similarity_search(query)
    print("Searching knowledge base ...",end='\n\n')
    res = chain.invoke({"input_documents": docs, "question": query})
    print(res["output_text"],end='\n\n')





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