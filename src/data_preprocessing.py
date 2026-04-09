import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in stop_words]
    return " ".join(words)

def load_data():
    fake = pd.read_csv("data/Fake.csv")
    true = pd.read_csv("data/True.csv")

    fake["label"] = 0
    true["label"] = 1

    df = pd.concat([fake, true])
    df = df.sample(frac=1).reset_index(drop=True)

    df["text"] = df["title"] + " " + df["text"]
    df["text"] = df["text"].apply(clean_text)

    return df[["text", "label"]]

if __name__ == "__main__":
    df = load_data()
    print(df.head())