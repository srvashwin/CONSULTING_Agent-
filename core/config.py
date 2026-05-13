import os
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")
warnings.filterwarnings("ignore", message=".*FutureWarning.*")
warnings.filterwarnings("ignore", message=".*past its end of life.*")

_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path=_env_path)


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    LLM_PROVIDER: str = "gemini" if GEMINI_API_KEY else ""

    GEMINI_MODEL_HEAVY: str = "gemini-2.5-pro"
    GEMINI_MODEL_LIGHT: str = "gemini-2.5-flash"

    CHROMA_PERSIST_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "chroma"
    )

    OUTPUT_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "output"
    )

    MAX_SEARCH_RESULTS: int = 8

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    MAX_TOKENS_HEAVY: int = 32000
    MAX_TOKENS_LIGHT: int = 8000


config = Config()
