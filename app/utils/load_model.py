import pandas as pd
import requests
from app.core.config import logger
from bertopic import BERTopic

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download&confirm=t"
    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

bert_topic_model = None
MODEL_PATH = "models/bertopic_model"

def get_bert_model():
    global bert_topic_model
    if bert_topic_model is not None:
        return bert_topic_model

    try:
        # 1. Load the model without the heavy transformer
        model = BERTopic.load(MODEL_PATH, embedding_model=None)

        # 2. Safety check for set_params
        # Only set n_jobs if it's a real UMAP/Parametric model, 
        # not the 'BaseDimensionalityReduction' placeholder
        if hasattr(model, "umap_model"):
            # Check specifically if set_params exists on the instance
            set_params_func = getattr(model.umap_model, "set_params", None)
            if callable(set_params_func):
                model.umap_model.set_params(n_jobs=1)
                logger.info("UMAP n_jobs set to 1.")

        bert_topic_model = model
        return bert_topic_model

    except Exception as e:
        # This logger is vital to see exactly why it failed in Celery logs
        logger.error(f"Error loading model: {str(e)}")
        return None


_shared_data = None
DATA_PATH = "models/bertopic_model/topic_info - topic_info.csv"

def get_topic_data():
    global _shared_data
    
    # 1. Return immediately if already loaded
    if _shared_data is not None:
        return _shared_data

    try:
        # 2. Load the CSV
        # Use specific columns if you don't need the whole file to save memory
        df = pd.read_csv(DATA_PATH)

        # Optional: Add any initial processing here 
        # (e.g., setting an index or dropping irrelevant columns)
        # df = df.set_index("id") 
        
        _shared_data = df
        logger.info("CSV data loaded successfully into memory.")
        return _shared_data

    except Exception as e:
        logger.error(f"Error loading CSV data: {str(e)}")
        return None
