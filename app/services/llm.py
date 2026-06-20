from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings

NO_CONTEXT_ANSWER = "I could not find enough indexed context to answer that question."

Answer_prompt = PromptTemplate.from_template(
    """
    Answer the question by only using supplied context.If the context does not
    contain the answer,say that you dont have enough information.Do not invent facts.
    
    Question: {question}
    Context: {context}
    
    Answer:"""
)

def get_llm()->ChatGoogleGenerativeAI():
    """Create the Gemini chat model used for RAG ans generation."""
    settings= get_settings()

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI API KEY is required but not provided")
    
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=settings.gemini_temparature,
    )

def generate_answer(question:str,contexts:list[dict])->str:
    context_text= "\n\n".join(context["content"] for context in contexts.strip())

    if not context_text:
        return NO_CONTEXT_ANSWER
    
    chain = Answer_prompt | get_llm() | StrOutputParser()
    return chain.invoke({"question":question,"context":context_text})