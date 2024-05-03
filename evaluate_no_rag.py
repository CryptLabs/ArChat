import langsmith
from langchain import chat_models, prompts, smith
from langchain.schema import output_parser


# Define your runnable or chain below.
prompt = prompts.ChatPromptTemplate.from_messages(
  [
    ("system", "You are a helpful AI assistant."),
    ("human", "{input}")
  ]
)
llm = chat_models.ChatOpenAI(model="gpt-4", temperature=0)
chain = prompt | llm | output_parser.StrOutputParser()

# Define the evaluators to apply
eval_config = smith.RunEvalConfig(
    evaluators=[
        "cot_qa"
    ],
    custom_evaluators=[],
    eval_llm=chat_models.ChatOpenAI(model="gpt-4", temperature=0)
)

client = langsmith.Client()
chain_results = client.run_on_dataset(
    dataset_name="archat_eval_dataset-1",
    llm_or_chain_factory=chain,
    evaluation=eval_config,
    project_name="Archat-NoRag-GPT-4",
    concurrency_level=5,
    verbose=True,
)