from softtek_llm.vectorStores import Vector, SupabaseVectorStore
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

vector_store = SupabaseVectorStore(
    api_key=SUPABASE_API_KEY,
    url=SUPABASE_URL,
    index_name=SUPABASE_INDEX_NAME,
)

def search(query, in_list = None):
    # print(query)
    res = vector_store.search(query)
    if in_list:
        res = [i for i in res if i.id in in_list]
    return res