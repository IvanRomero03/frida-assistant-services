import logging
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import gcsfs
from bs4 import BeautifulSoup
import requests
from Embeddings.save import save_embedding_from_text, get_embeddings_from_text
from Embeddings.analyze import get_text_sumary, get_text_keywords, get_most_relevant_sentences, get_text_analysis
from Embeddings.analyze import analyze_text
from Embeddings.search import search
from softtek_llm.vectorStores import Vector, SupabaseVectorStore
from softtek_llm.chatbot import Chatbot
from softtek_llm.models import OpenAI
from softtek_llm.cache import Cache
from softtek_llm.embeddings import OpenAIEmbeddings
from flask_cors import CORS
import io
from dotenv import load_dotenv
import os

app = Flask(__name__)
CORS(app)

@app.route("/api/test")
def test():
    return jsonify({"message": "Hello World!"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route("/api/pdf_scrapper", methods=["POST"])
def parse_pdf():
    gcs_pdf_path = request.get_json()["gcs_pdf_path"]
    print(gcs_pdf_path)
    #works url gsutil url
    parsed_text = ""
    response = requests.get(gcs_pdf_path)
    with io.BytesIO(response.content) as f_object:
        pdf = PdfReader(f_object)
        number_of_pages = len(pdf.pages)
        
        for i in range (number_of_pages):
            page = pdf.pages[i]
            parsed_text = parsed_text + page.extract_text() + "\n"
        
    return jsonify({"text": parsed_text})

@app.route("/api/web_scrapper", methods=["POST"])
# URL of the page to be scraped
def scrap_text():
    url = request.get_json()["url"]
    # Retrieve page with the requests module
    response = requests.get(url)

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = BeautifulSoup(response.text, 'html.parser')

    parsed_text = ""
    # Print all paragraph texts
    for par in soup.find_all(['h1','h2','p','table']):
        parsed_text = parsed_text + par.text + "\n" 

    return jsonify({"text": parsed_text})    


@app.route("/api/save_embeddings")
def save_embeddings():
    text = request.get_json()["text"]
    res = save_embedding_from_text(text)
    return jsonify(res)

@app.route("/api/get_embeddings", methods=["POST"])
def get_embeddings():
    text = request.get_json()["text"]
    print(text)
    res = get_embeddings_from_text(text)
    return jsonify({"emb":res})

@app.route("/api/get_sumary")
def get_sumary():
    id = request.get_json()["id"]
    res = get_text_sumary(id)
    return jsonify(res.content)

@app.route("/api/get_keywords")
def get_keywords():
    id = request.get_json()["id"]
    res = get_text_keywords(id)
    return jsonify(res)

@app.route("/api/relevant_sentences")
def relevant_sentences():
    id = request.get_json()["id"]
    res = get_most_relevant_sentences(id)
    return jsonify(res)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    text = request.get_json()["text"]
    print(text) 
    res = analyze_text(text)
    return jsonify(res)

@app.route("/api/get_search", methods=["POST"])
def get_search():
    query = request.get_json()["query"]
    print(query)
    if query == "":
        print("EMPTY")
        return jsonify({"ids": []})
    print(query)
    query = Vector(embeddings=get_embeddings_from_text(query))
    res = search(query=query)
    print({"ids": [i.id for i in res]})
    return jsonify({"ids": [i.id for i in res]})

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise ValueError("OPENAI_API_KEY not found in .env file")

OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
if OPENAI_API_BASE is None:
    raise ValueError("OPENAI_API_BASE not found in .env file")

OPENAI_EMBEDDINGS_MODEL_NAME = os.getenv("OPENAI_EMBEDDINGS_MODEL_NAME")
if OPENAI_EMBEDDINGS_MODEL_NAME is None:
    raise ValueError("OPENAI_EMBEDDINGS_MODEL_NAME not found in .env file")

OPENAI_CHAT_MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL_NAME")
if OPENAI_CHAT_MODEL_NAME is None:
    raise ValueError("OPENAI_CHAT_MODEL_NAME not found in .env file")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
if not SUPABASE_API_KEY:
    raise ValueError("SUPABASE_API_KEY is not set")
SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL is not set")
SUPABASE_INDEX_NAME = os.getenv("SUPABASE_INDEX_NAME")
if not SUPABASE_INDEX_NAME:
    raise ValueError("SUPABASE_INDEX_NAME is not set")

embeddings_model = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model_name=OPENAI_EMBEDDINGS_MODEL_NAME,
    api_type="azure",
    api_base=OPENAI_API_BASE,
)
vector_store = SupabaseVectorStore(
    api_key=SUPABASE_API_KEY,
    url=SUPABASE_URL,
    index_name=SUPABASE_INDEX_NAME,
)
cache = Cache(vector_store=vector_store, embeddings_model=embeddings_model)
model = OpenAI(
    api_key=OPENAI_API_KEY,
    model_name=OPENAI_CHAT_MODEL_NAME,
    api_type="azure",
    api_base=OPENAI_API_BASE,
    verbose=True,
)
chatbot = Chatbot(
    model=model,
    description="Test Chatbot",
    cache=cache,
    verbose=True,
)

@app.route("/api/chatbot_reset", methods=["POST"])
def chatbot_reset():
    global chatbot
    chatbot = Chatbot(
        model=model,
        description="Test Chatbot",
        cache=cache,
        verbose=True,
    )
    return jsonify({"message": "Chatbot reseted"})

@app.route("/api/chatbot", methods=["POST"])
def chatbotaaa():
    query = request.get_json()["query"]
    chatbot_response = chatbot.chat(query)
    return jsonify({"response": chatbot_response.message.content})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)
