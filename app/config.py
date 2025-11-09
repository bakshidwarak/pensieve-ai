from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pensieve"
    OPENAI_API_KEY: str | None = None
    PINECONE_API_KEY: str | None = None
    PINECONE_ENV: str | None = None
    PINECONE_INDEX: str = "pensieve-notes"
    USE_PINECONE: bool = False
    API_KEYS: str = "dev-key"
    VECTOR_DIM: int = 1536
    FAISS_PATH: str = "./data/faiss_store"

    class Config:
        env_file = ".env"

settings = Settings()
