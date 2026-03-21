import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "1our9mc-TVwYpdiVS6NtQTwde3tCziYz0OtCWBQxQgig"

def get_sheet():
    try:
        import streamlit as st
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    except Exception:
        creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID).sheet1

def log_question(question: str, response: str, language: str = "English", cuisine: str = "Any", diet: str = "Any"):
    try:
        sheet = get_sheet()
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            language,
            question,
            cuisine,
            diet,
            response[:500]
        ])
    except Exception as e:
        print(f"Logging failed: {str(e)}")
