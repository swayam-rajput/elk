from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
    GITHUB_REPO = os.getenv("GITHUB_REPO")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")