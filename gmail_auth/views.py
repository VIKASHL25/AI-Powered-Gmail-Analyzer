from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os, base64, re, pickle
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from transformers import pipeline

#  Google OAuth Configuration
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "cred.json")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
REDIRECT_URI = 'http://localhost:8000/google/callback/'

MODEL_PATH = os.path.join(settings.BASE_DIR, "gmail_auth", "email_classifier.pkl")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


def get_email_body(payload):

    def decode_data(data):
        return base64.urlsafe_b64decode(data).decode(errors="ignore")

    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            body = part.get("body", {}).get("data")
            if body and ("text/plain" in mime_type or "text/html" in mime_type):
                return decode_data(body)
    else:
        data=payload.get("body", {}).get("data")
        if data:
            return decode_data(data)
    return ""


def home(request):
    return render(request, "login.html")


def google_login(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    return redirect(f"{authorization_url}&custom_state={state}")


def google_callback(request):
   
    state = request.GET.get('state') or request.GET.get('custom_state')
    if not state:
        state='devstate' 

    flow=Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri=REDIRECT_URI
    authorization_response = request.build_absolute_uri()

    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        return HttpResponse(f"Authorization failed: {str(e)}")

    credentials = flow.credentials


    with open('token.json', 'w') as token:
        token.write(credentials.to_json())


    service=build('gmail', 'v1', credentials=credentials)
    result=service.users().messages().list(userId='me', maxResults=20).execute()
    messages=result.get('messages', [])


    if not os.path.exists(MODEL_PATH):
        return HttpResponse("Email classifier not found. Please train the model first.")

    with open(MODEL_PATH, 'rb') as f:
        clf = pickle.load(f)

    email_data=[]

    for msg in messages:
        msg_detail=service.users().messages().get(userId='me', id=msg['id']).execute()
        headers=msg_detail['payload'].get('headers', [])
        subject=next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender=next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        snippet=msg_detail.get('snippet', '')
        body=get_email_body(msg_detail['payload'])
        clean_body = re.sub(r'\s+', ' ', body)

       
        try:
            importance = clf.predict([clean_body])[0]
        except Exception:
            importance = "Unknown"

        summary=""
        word_count = len(clean_body.split())
        if 40 < word_count < 1000:
            try:
                result = summarizer(clean_body, max_length=80, min_length=30, do_sample=False)
                summary = result[0]['summary_text'].strip()
            except Exception:
                summary = ""

        email_data.append({
            'subject': subject,
            'sender': sender,
            'snippet': snippet,
            'importance': importance,
            'summary': summary,
        })

    return render(request, 'email.html', {'emails': email_data})
