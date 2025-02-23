from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import db_helper  # Ensure this is correct
import re

app = FastAPI()

def extract_session_id(session_str: str):
    # Regex pattern to extract session ID
    pattern = r"projects/[^/]+/agent/sessions/([^/]+)/contexts/[^/]+"

    # Perform regex search
    match = re.search(pattern, session_str)
    if match:
        extracted_string = match.group(1)
        return extracted_string
    return ""

def get_str_from_movie_dict(movie_dict:dict):
    return ", ".join([f"{int(value)}{key}" for key, value in movie_dict.items()])


