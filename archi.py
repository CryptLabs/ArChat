import os
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
        config["question"] = (
            "What is the the best editor for the terminal in Arch Linux?"
        )

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

# print(config['Arch_Linux_Data_Sources'])


# Load an LLM
def load_llm(llm_type):
    if llm_type == "ChatOpenAI":
        llm = ChatOpenAI(
            temperature=0.5,
            model="gpt-4",
            openai_api_key="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",
        )
    elif llm_type == "GPT4All":
        llm = GPT4All(
            model=r"/home/al1nux/Projects/models/orca-mini-3b-gguf2-q4_0.gguf",
            max_tokens=2048,
        )
    else:
        raise ValueError("Invalid LLM type")
    return llm


def create_chat_prompt(query):
    template = """You are a helpful Arch Linux assistant that answers {question} by finding answers from {input_documents}.
        """
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

    vectordb = Chroma(
        persist_directory=config["data_dir"], embedding_function=embeddings
    )

    docs = vectordb.similarity_search(query)

    return docs


def get_answer(llm, chat_prompt, query):
    chain = load_qa_chain(llm, chain_type="stuff")
    res = chain.invoke(
        {
            "prompt": chat_prompt,
            "input_documents": search_knowledge_base(query),
            "question": query,
        }
    )
    #
    return res["output_text"]
