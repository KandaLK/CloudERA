from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List

class Settings(BaseSettings):
    model_config = {"env_file": "../.env", "extra": "allow"}
    
    # Database Configuration
    database_url: str = Field(default="postgresql://cloud_era_user:cloud_era_password@localhost:5432/cloud_era_db", alias="BACKEND_DATABASE_URL")
    
    # JWT Settings
    secret_key: str = Field(default="your-secret-key-change-in-production", alias="BACKEND_SECRET_KEY")
    algorithm: str = "HS256" 
    access_token_expire_minutes: int = Field(default=1440, alias="BACKEND_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Server Settings
    host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    port: int = Field(default=8000, alias="BACKEND_PORT")
    debug: bool = Field(default=False, alias="BACKEND_DEBUG")
    
    # API Settings
    api_title: str = "Cloud ERA Agent Chatbot API"
    api_version: str = "1.0.0"
    
    # CORS Settings  
    cors_origins: List[str] = Field(default=["http://localhost:5173", "http://localhost:3000"], alias="BACKEND_CORS_ORIGINS")
    
    # OpenAI Settings
    openai_api_key: Optional[str] = Field(default=None, alias="SHARED_OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="SHARED_OPENAI_MODEL")
    
    # Web Search APIs
    tavily_api_key: Optional[str] = Field(default=None, alias="SHARED_TAVILY_API_KEY")
    jina_api_key: Optional[str] = Field(default=None, alias="SHARED_JINA_API_KEY")
    
    # Neo4j Database
    neo4j_uri: str = Field(default="neo4j://localhost:7687", alias="SHARED_NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", alias="SHARED_NEO4J_USERNAME")
    neo4j_password: str = Field(default="your-password-here", alias="SHARED_NEO4J_PASSWORD")
    
    # Multi-Agent System Settings
    vector_db_path: str = "./data/chroma_db"
    stm_token_limit: int = 4000
    ltm_update_interval: int = 20
    max_iterations: int = 3
    max_concurrent_users: int = Field(default=10, alias="BACKEND_MAX_CONCURRENT_USERS")
    
    # Web Search Settings
    web_search_max_results: int = Field(default=5, alias="SHARED_WEB_SEARCH_MAX_RESULTS")
    web_scraping_token_limit: int = Field(default=20000, alias="SHARED_WEB_SCRAPING_TOKEN_LIMIT")
    web_search_timeout: int = Field(default=30, alias="SHARED_WEB_SEARCH_TIMEOUT")
    
    # URL Confidence & Selection Settings
    url_confidence_threshold: float = 0.6
    tavily_results_per_query: int = 5
    top_urls_to_scrape: int = Field(default=5, alias="SHARED_TOP_URLS_TO_SCRAPE")
    max_fallback_urls: int = 8
    url_retry_attempts: int = 2
    
    # JINA Scraping Settings
    jina_scraping_timeout: int = 60
    jina_connect_timeout: int = 10
    jina_read_timeout: int = 50
    scraping_max_concurrent: int = 3
    scraping_max_urls: int = 5
    
    # LIGHTRAG Knowledge Base Settings
    lightrag_working_dir: str = Field(default="./data/cloud_kb_storage", alias="SHARED_LIGHTRAG_WORKING_DIR")
    lightrag_documents_dir: str = "./documents"
    lightrag_llm_model: str = "gpt-4o-mini"
    lightrag_embedding_model: str = "text-embedding-3-large"
    
    # Translation Service (DeepSeek API - Optional)
    deepseek_api_key: Optional[str] = Field(default=None, alias="SHARED_DEEPSEEK_API_KEY")
    deepseek_model: str = "deepseek-chat"
    translation_enabled: bool = True

settings = Settings()