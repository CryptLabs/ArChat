import os
print(os.getcwd())

import sys
import argparse
import yaml
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings



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
        config["mediawikis"] = ["archwiki"]
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
print(config['mediawikis'])

## Use chromadb to get the data 

embeddings = HuggingFaceEmbeddings(
        cache_folder="./model",
        model_name=config["embeddings_model"],
        show_progress=True,
)
# query it
query = "how can we update grub?"

# load from disk
vectordb = Chroma(persist_directory=config["data_dir"], embedding_function=embeddings)
docs = vectordb.similarity_search(query)
print(docs[0].page_content)

