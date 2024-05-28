############################################
import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import GPT4All
from langchain import hub
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import ChatOpenAI
from langchain_core.prompts.chat import ChatPromptTemplate
import archat
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.evaluation import EvaluatorType
from langchain.smith import RunEvalConfig, run_on_dataset
from langsmith import Client
from langsmith.utils import LangSmithError
from langchain.chains import RetrievalQA

import openai

openai.api_key = os.environ["OPENAI_API_KEY"]

LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")

embeddings = HuggingFaceEmbeddings(
    cache_folder="./model",
    model_name=archat.config["embeddings_model"],
    show_progress=False,
)

vectordb = Chroma(
    persist_directory=archat.config["data_dir"], embedding_function=embeddings
)


retriever = vectordb.as_retriever(search_kwragssearch_kwargs={"k": 10})
# retriever = vectordb.similarity_search(query)
# search_kwragssearch_kwargs={"k": 3}


prompt_template = """
Answer the question based only on the supplied context. If you don't know the answer, say you don't know the answer.
Context: {context}
Question: {question}
Your answer:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)
model = ChatOpenAI(openai_api_key=openai.api_key)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)

print(chain.invoke("In the given context, what is pacman?"))

# Our evaluation dataset

model = ChatOpenAI(openai_api_key=openai.api_key)

eval_questions = [
    "What is Pacman?",
    "When was the birth of the ArchWiki?",
    "How can I Acquire build files?",
    "Arch needs an installer. Maybe a GUI installer?",
    "How do I install and upgrade packages using AUR?",
    "A package update was released, but pacman says the system is up to date. What should I do?",
    "Is Arch Linux a stable distribution? Will I get frequent breakage?",
    "I am a complete GNU/Linux beginner. Should I use Arch?",
    "Where can I find the Arch Linux Repositories?",
    "What is the Arch User Repository?",
]

eval_answers = [
    "Pacman is the package manager used in Arch Linux. It is designed to easily manage packages, whether they are from official repositories or user-built packages. Pacman keeps the system up-to-date by synchronizing package lists with the master server and allows users to download/install packages with a simple command, handling dependencies automatically.",
    "On 2005-07-08 the ArchWiki was first set up on the MediaWiki engine.",
    "Locate the package in the AUR. This is done using the search field at the top of the AUR home page. Clicking the application's name in the search list brings up an information page on the package. Read through the description to confirm that this is the desired package, note when the package was last updated, and read any comments.",
    "Arch used to have an installer with a text-based user interface called the Arch Installation Framework (AIF). After its last maintainer left, it was deprecated in favor of arch-install-scripts. Since 2021-04-01, Arch has an installer again. See archinstall for details.",
    "Installing packages from the AUR is a relatively simple process. Essentially: Acquire the build files, including the PKGBUILD and possibly other required files, like systemd units and patches (often not the actual code). Verify that the PKGBUILD and accompanying files are not malicious or untrustworthy.Run makepkg in the directory where the files are saved. This will download the code, compile it, and package it. Run pacman -U package_file to install the package onto your system.",
    "pacman mirrors are not synced immediately. It may take over 24 hours before an update is available to you. The only options are be patient or use another mirror. MirrorStatus can help you identify an up-to-date mirror.",
    "It is the user who is ultimately responsible for the stability of their own rolling release system. The user decides when to upgrade, and merges necessary changes when required. If the user reaches out to the community, help is often provided in a timely manner. The difference between Arch and other distributions in this regard is that Arch is truly a 'do-it-yourself' distribution; complaints of breakage are misguided and unproductive, since upstream changes are not the responsibility of Arch devs. See the System maintenance article for tips on how to make an Arch Linux system as stable as possible.",
    "If you are a beginner and want to use Arch, you must be willing to invest time into learning a new system, and accept that Arch is designed as a 'do-it-yourself' distribution; it is the user who assembles the system. Before asking for help, do your own independent research by searching the Web, the forum and the superb documentation provided by the Arch Wiki. There is a reason these resources were made available to you in the first place. Many thousands of volunteered hours have been spent compiling this excellent information. See also Arch terminology#RTFM and the Installation guide.",
    "The Arch Linux Repositories can be found in the /repos directory of the Arch Linux Archive. The repositories contain daily snapshots of the official mirror organized by date.",
    "While the Arch Build System allows the ability of building software available in the official repositories, the Arch User Repository (AUR) is the equivalent for user submitted packages. It is an unsupported repository of build scripts accessible through the web interface or through the Aurweb RPC interface.",
]

examples = zip(eval_questions, eval_answers)

client = Client()
dataset_name = "ArChat_eval_dataset-2"

try:
    dataset = client.read_dataset(dataset_name=dataset_name)
    print("using existing dataset: ", dataset.name)
except LangSmithError:
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="sample evaluation dataset",
    )
    for question, answer in examples:
        client.create_example(
            inputs={"input": question},
            outputs={"answer": answer},
            dataset_id=dataset.id,
        )

    print("Created a new dataset: ", dataset.name)


def create_qa_chain(llm, vectordb, return_context=True):
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=return_context,
    )
    return qa_chain


# Evaluation configuration
evaluation_config = RunEvalConfig(
    evaluators=[
        "qa",
        "context_qa",
        "cot_qa",
    ],
    prediction_key="result",
)

# client = Client()
run_on_dataset(
    dataset_name=dataset_name,
    llm_or_chain_factory=create_qa_chain(llm=model, vectordb=vectordb),
    client=client,
    # project_name="ArChat-RAG-GPT-4",
    evaluation=evaluation_config,
    verbose=True,
)
