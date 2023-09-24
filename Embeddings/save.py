from softtek_llm.embeddings import OpenAIEmbeddings
from softtek_llm.vectorStores import SupabaseVectorStore
from softtek_llm.vectorStores import Vector
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
if not SUPABASE_API_KEY:
    raise ValueError("SUPABASE_API_KEY is not set")
SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is not set")
SUPABASE_INDEX_NAME = os.getenv("SUPABASE_INDEX_NAME")
if not SUPABASE_INDEX_NAME:
    raise ValueError("SUPABASE_INDEX_NAME is not set")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")
OPENAI_EMBEDDINGS_MODEL_NAME = os.getenv("OPENAI_EMBEDDINGS_MODEL_NAME")
if not OPENAI_EMBEDDINGS_MODEL_NAME:
    raise ValueError("OPENAI_EMBEDDING_MODEL_NAME is not set")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
if not OPENAI_API_BASE:
    raise ValueError("OPENAI_API_BASE is not set")

def get_embeddings_from_text(text):
    embeddings_model = OpenAIEmbeddings(
        api_key=OPENAI_API_KEY,
        model_name=OPENAI_EMBEDDINGS_MODEL_NAME,
        api_type="azure",
        api_base=OPENAI_API_BASE,
    )
    return embeddings_model.embed(text)

def save_embedding_from_text(text, id = None):
    vector_store = SupabaseVectorStore(
        api_key=SUPABASE_API_KEY,
        url=SUPABASE_URL,
        index_name=SUPABASE_INDEX_NAME,
    )
    emb = get_embeddings_from_text(text)
    new_vector = Vector(embeddings=emb, id=id)
    res = vector_store.add(vectors=[new_vector])
    return [{"id": i.id} for i in res]


