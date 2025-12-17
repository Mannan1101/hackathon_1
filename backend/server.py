from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents import Agent, Runner, OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from agents import set_tracing_disabled, function_tool
import os
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient

load_dotenv()
set_tracing_disabled(disabled=True)

app = FastAPI()

# CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

# Initialize Cohere client
cohere_client = cohere.Client("oUuAl4v8wIgcjVi5jXMCPNMsh5KsbiIuXzMHJStg")

# Connect to Qdrant
qdrant = QdrantClient(
    url= os.getenv("QUDRANT_URL"),
    api_key = os.getenv("QUDRANT_API_KEY")
                        
)

COLLECTION_NAME = "humanoid_ai_book"

def get_embedding(text):
    """Get embedding vector from Cohere Embed v3"""
    response = cohere_client.embed(
        model="embed-english-v3.0",
        input_type="search_query",
        texts=[text],
    )
    return response.embeddings[0] # type: ignore

@function_tool
def retrieve(query):
    """Retrieve relevant content from the knowledge base"""
    embedding = get_embedding(query)
    result = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        limit=5
    )
    return [point.payload["text"] for point in result.points if point.payload and "text" in point.payload]

# Create agent
agent = Agent(
    name="Assistant",
    instructions="""
You are an AI tutor for the Physical AI & Humanoid Robotics textbook.
To answer the user question, first call the tool `retrieve` with the user query.
Use ONLY the returned content from `retrieve` to answer.
If the answer is not in the retrieved content, say "I don't know".
""",
    model=model,
    tools=[retrieve]
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint that processes user questions"""
    try:
        result = Runner.run_sync(
            agent,
            input=request.question,
        )
        return ChatResponse(answer=result.final_output)
    except Exception as e:
        return ChatResponse(answer=f"Error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Backend server is running"}
