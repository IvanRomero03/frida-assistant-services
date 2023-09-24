import logging
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import gcsfs
from bs4 import BeautifulSoup
import requests
from Embeddings.save import save_embedding_from_text, get_embeddings_from_text

app = Flask(__name__)

@app.route("/api/test")
def test():
    return jsonify({"message": "Hello World!"})

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.route("/api/pdf_scrapper")
def parse_pdf():
    gcs_pdf_path = request.get_json()["gcs_pdf_path"]
    #works url gsutil url
    gcs_file_system = gcsfs.GCSFileSystem(project="frida-file-bucket", token="credentials.json")

    f_object = gcs_file_system.open(gcs_pdf_path, "rb")
    pdf = PdfReader(f_object)
    number_of_pages = len(pdf.pages)
    parsed_text = ""

    for i in range (number_of_pages):
        page = pdf.pages[i]
        parsed_text = parsed_text + page.extract_text() + "\n"
    
    return jsonify({"text": parsed_text})

@app.route("/api/web_scrapper")
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
        parsed_text = parsed_text + par.name + " : " + par.text + "\n" 

    return jsonify({"text": parsed_text})    

@app.route("/api/save_embeddings")
def save_embeddings():
    text = request.get_json()["text"]
    res = save_embedding_from_text(text)
    return jsonify(res)

@app.route("/api/get_embeddings")
def get_embeddings():
    text = request.get_json()["text"]
    print(text)
    res = get_embeddings_from_text(text)
    return jsonify({"pls":res})

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=5000)