import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

from .config import TEMP_DIR, GROQ_API_KEY

os.makedirs(TEMP_DIR, exist_ok=True)

Groq_Client = Groq(api_key=GROQ_API_KEY)

# This is a global variable
vector_store = None  

def update_vector_store(new_vector_store):
    global vector_store
    vector_store = new_vector_store

def get_vector_store():
    return vector_store
