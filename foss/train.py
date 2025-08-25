import pandas as pd
import re
from transformers import FNetModel, FNetTokenizer
from langdetect import detect
from googletrans import Translator
import torch

# 1) Load CSV
df = pd.read_csv("amazon_reviews.csv")
print("Columns in file:", df.columns)

# 2) Clean text
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    return text.strip()

df['cleaned_text'] = (df['reviewText'].fillna("") + " " + df['summary'].fillna("")).map(clean_text)

# 3) Detect language and translate Tamil → English
translator = Translator()
printed_demo = False  # Flag to print only once

def detect_and_translate(text):
    global printed_demo
    try:
        if not text.strip():
            return ""
        lang = detect(text)
        if lang == 'ta':
            translated = translator.translate(text, src='ta', dest='en').text
            if not printed_demo:
                print(f"Tamil Review: {text}\n→ English: {translated}\n")
                printed_demo = True
            return translated
        else:
            return text
    except:
        return text

df['en_text'] = df['cleaned_text'].map(detect_and_translate)

# 4) FNet Embeddings
tokenizer = FNetTokenizer.from_pretrained("google/fnet-base")
model = FNetModel.from_pretrained("google/fnet-base")

def fnet_embedding(text):
    if not isinstance(text, str) or text.strip() == "":
        return torch.zeros(model.config.hidden_size)
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1).squeeze()
    return embedding

df['fnet_embedding'] = df['en_text'].apply(lambda x: fnet_embedding(x).numpy())

# 5) Save processed data for later use
df.to_pickle("processed_reviews.pkl")
print("✅ Training/Preprocessing done. Saved to processed_reviews.pkl")

