import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MODEL_NAME = os.getenv("LLM_MODEL", "gpt-6-luna")
MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))

def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=MODEL_NAME)