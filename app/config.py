from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_dir: str = "./data"
    db_url: str = "sqlite:///./data/finrag.sqlite"
    faiss_index_path: str = "./data/faiss.index"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    top_k: int = 5
    idk_threshold: float = 0.28

    llm_provider: str = "ollama"  # ollama | openai | none
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"


settings = Settings()
