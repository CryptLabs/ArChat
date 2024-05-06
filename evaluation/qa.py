from langchain.chat_models import ChatAnthropic
from langchain_core.prompts.prompt import PromptTemplate
from langsmith.evaluation import LangChainStringEvaluator
import archat

_PROMPT_TEMPLATE = """You are an expert professor specialized in grading students' answers to questions.
You are grading the following question:
{input}
Here is the real answer:
{reference}
You are grading the following predicted answer:
{prediction}
Respond with CORRECT or INCORRECT:
Grade:
"""

PROMPT = PromptTemplate(
    input_variables=["input", "reference", "prediction"], template=_PROMPT_TEMPLATE
)
eval_llm = ChatAnthropic(temperature=0.0)

qa_evaluator = LangChainStringEvaluator("qa", config={"llm": eval_llm, "prompt": PROMPT})  
context_qa_evaluator = LangChainStringEvaluator("context_qa", config={"llm": eval_llm})
cot_qa_evaluator = LangChainStringEvaluator("cot_qa", config={"llm": eval_llm})
evaluate(
    <yourpipeline>,
    data="<dataset_name>",
    evaluators=[qa_evaluator, context_qa_evaluator, cot_qa_evaluator],  
)