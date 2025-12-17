import cohere
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import os
# Initialize Cohere client
cohere_client = cohere.Client("oUuAl4v8wIgcjVi5jXMCPNMsh5KsbiIuXzMHJStg")

# Connect to Qdrant
qdrant = QdrantClient(
    url= os.getenv("QUDRANT_URL"),
    api_key= os.getenv("AQUDRANT_API_KEY")
)

def get_embedding(text):
    """Get embedding vector from Cohere Embed v3"""
    response = cohere_client.embed(
        model="embed-english-v3.0",
        input_type="search_query",  # Use search_query for queries
        texts=[text],
    )
    if hasattr(response, 'embeddings') and isinstance(response.embeddings, list) and len(response.embeddings) > 0:
        return response.embeddings[0]
    else:
        raise ValueError("Failed to get embedding from Cohere. The response did not contain any embeddings.")

def retrieve(query):
    embedding = get_embedding(query)
    result = qdrant.query_points(
        collection_name="humanoid_ai_book",
        query=embedding,
        limit=5
    )
    return [point.payload["text"] for point in result.points if point.payload and "text" in point.payload]

# Test
print(retrieve("What data do you have?"))
