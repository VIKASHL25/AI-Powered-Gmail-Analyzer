import os
import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "emails_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "email_classifier.pkl")

def train_email_classifier():
   

    if not os.path.exists(DATASET_PATH):
        print(" Dataset not found. Please add emails_dataset.csv in gmail_auth/")
        return

    df=pd.read_csv(DATASET_PATH)
    X=df["text"]
    y=df["label"]

    X_train, X_test, y_train, y_test=train_test_split(X, y, test_size=0.2, random_state=42)

    model=make_pipeline(TfidfVectorizer(stop_words='english'), MultinomialNB())
    model.fit(X_train, y_train)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Model trained ")

if __name__ == "__main__":
    train_email_classifier()
