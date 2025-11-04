from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Path to your Google Cloud credentials JSON
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, "cred.json")

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Redirect URI (must match Google Cloud Console exactly)
REDIRECT_URI = 'http://localhost:8000/google/callback/'

def home(request):
    """Homepage with login link"""
    return render(request, "login.html")

def google_login(request):
    """Start the OAuth2 flow"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
   # Generating authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )

    
    request.session['state'] = state
    return redirect(authorization_url)


def google_callback(request):
 
    state = request.session.get('state')

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    
    with open('token.json', 'w') as token:
        token.write(credentials.to_json())

    # Connecting to Gmail API
    service = build('gmail', 'v1', credentials=credentials)

    # Fetching messages
    result = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = result.get('messages', [])

    email_data = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        snippet = msg_detail.get('snippet', '')
        email_data.append({
            'subject': subject,
            'sender': sender,
            'snippet': snippet,
        })

    return render(request, 'email.html', {'emails': email_data})


def fetch_emails(request):
    """Fetch Gmail messages using saved token.json"""
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        return HttpResponse("No valid credentials. Please log in first.")

    service = build('gmail', 'v1', credentials=creds)

    try:
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])

        email_subjects = []
        if not messages:
            email_subjects.append('No messages found.')
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                snippet = msg.get('snippet', '(No snippet)')
                email_subjects.append(snippet)

        return HttpResponse('<br><br>'.join(email_subjects))

    except Exception as e:
        return HttpResponse(f"An error occurred: {str(e)}")
