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
