import os
import gdown

def download_model_from_gdrive():
    model_path = "model/tinyllama.gguf"
    if not os.path.exists(model_path):
        print("Downloading TinyLlama model from Google Drive...")
        file_id = "11LS30Nt6zSZN-x88PY-7fqRNHPS-1U0G"
        url = f"https://drive.google.com/uc?id={file_id}"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        gdown.download(url, model_path, quiet=False)
    else:
        print("Model already exists. Skipping download.")
