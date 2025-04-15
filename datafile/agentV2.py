# agentV2.py

from google.cloud import aiplatform
import os
from dotenv import load_dotenv
from vectorSearch import get_content_from_bigquery
from langchain_google_vertexai import VertexAI


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "carbon-beanbag-452610-q6-53b220c17831.json"
aiplatform.init(project="carbon-beanbag-452610-q6")

llm = VertexAI(model_name="gemini-2.0-flash")

def rag_response(user_question):
    print("User question:", user_question)
    print("ENTERED THE RAG RESPONSE FUNCTIONALITY")
    data = get_content_from_bigquery(user_question)
    
    prompt = f"""You are a helpful assistant that only answers based on the provided context. Do not use any outside knowledge. If the answer is not in the context, reply with "I don't know based on the provided information."
    Context:
    {data}
    Question:
    {user_question}
    Answer (based strictly on the context):
    """

    output = llm.invoke([prompt])
    return output
