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
import archi
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
    model_name=archi.config["embeddings_model"],
    show_progress=False,
)

vectordb = Chroma(
    persist_directory=archi.config["data_dir"], embedding_function=embeddings
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

print(chain.invoke(
    "In the given context, what is pacman?"
))

####

model = ChatOpenAI(openai_api_key=openai.api_key)

eval_questions = [
    "What is Pacman?",
]

eval_answers = [
    "Pacman is the package manager used in Arch Linux. It is designed to easily manage packages, whether they are from official repositories or user-built packages. Pacman keeps the system up-to-date by synchronizing package lists with the master server and allows users to download/install packages with a simple command, handling dependencies automatically.",
]

examples = zip(eval_questions, eval_answers)

client = Client()
dataset_name = "archat_eval_dataset-1"

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

#client = Client()
run_on_dataset(
    dataset_name=dataset_name,
    llm_or_chain_factory=create_qa_chain(llm=model, vectordb=vectordb),
    client=client,
    project_name="Archat-RAG-GPT-4",
    evaluation=evaluation_config,
    verbose=True,
)
