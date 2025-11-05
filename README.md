# Smart MailSense — AI-Powered Gmail Analyzer

Smart MailSense is an intelligent Gmail analyzer built with Django, Google OAuth2, and AI/ML components to classify and summarize recent emails. It connects securely to Gmail, fetches recent messages, classifies them as Important or Non-Important, and generates concise AI summaries.

## Key Features

- Secure Google OAuth2 authentication
- Fetches up to 15 latest Gmail messages
- Local AI/ML classification (Important vs Non-Important)
- AI-generated summaries using transformer models
- Modern responsive UI built with HTML and CSS
- Local model storage for reusability
- End-to-end Django integration with SQLite default database

## Tech Stack

- Frontend: HTML5, CSS3
- Backend: Django (Python)
- AI/ML: scikit-learn, Transformers (Hugging Face)
- APIs: Gmail API, Google OAuth 2.0
- Database: SQLite (default Django DB)

## Project Structure

```
SmartMailSense/
├── googleauth/                  # Main Django project folder
├── gmail_auth/                  # Django app
│   ├── templates/
│   │   ├── login.html
│   │   └── email.html
│   ├── views.py
│   ├── urls.py
│   ├── train_model.py
│   └── email_classifier.pkl
├── cred.json                    # Google OAuth credentials (rename after download)
├── token.json                   # Generated after login
├── requirements.txt
├── manage.py
└── README.md
```

## Requirements

Suggested `requirements.txt` entries:

```
Django==5.2.7
google-auth==2.36.0
google-auth-oauthlib==1.2.1
google-api-python-client==2.158.0
transformers==4.44.2
torch==2.4.1
scikit-learn==1.5.2
numpy==1.26.4
pandas==2.2.3
requests==2.32.3
```

## Setup Instructions

1. Clone the repository

```powershell
git clone https://github.com/yourusername/smart-mailsense.git
cd smart-mailsense
```

2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1


3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Create `cred.json` (Google OAuth credentials)

Steps:

- Go to the Google Cloud Console and create a new project.
- Enable the Gmail API for your project.
- Create OAuth 2.0 Client ID credentials (application type: Web application).
- Add `http://localhost:8000/google/callback/` as an Authorized Redirect URI.
- Download the JSON credentials file and rename it to `cred.json` and place it in the project root.

5. Run database migrations and start the server

```powershell
python manage.py migrate
python manage.py runserver
```

Open your browser at: http://127.0.0.1:8000 and log in with Google to start analyzing your inbox.

## AI Functionality

### Email Classification

A locally trained classifier (`email_classifier.pkl`) labels emails as:

- Important
- Non-Important

The model can be retrained on your dataset (an example CSV dataset is expected by the training script).

### Email Summarization

Uses a transformer summarization model (for example `facebook/bart-large-cnn`) to generate concise summaries of longer messages.

## Training the Classifier

To retrain the importance classifier, run:

```powershell
python gmail_auth/train_model.py
```

This script reads training data (e.g., `email_dataset.csv`), trains a classification model (Logistic Regression or Naive Bayes), and saves the trained model to `email_classifier.pkl`.


## Screenshots
#### 🔹 Login Page
 
![Login Page](./imgs/login.png)

#### 🔹 Dashboard View
![Dashboard](./imgs/mails.png)





