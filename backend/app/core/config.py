from typing import List, Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=False)

    # Database
    database_url: str = "postgresql://user:password@localhost:5435/citycamp_db"
    database_host: str = "localhost"
    database_port: int = 5435
    database_name: str = "citycamp_db"
    database_user: str = "user"
    database_password: str = "password"

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # External APIs
    openai_api_key: Optional[str] = None
    geocodio_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None

    # Google Custom Search API
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_s3_bucket: str = "citycamp-assets"

    # Vector Database
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "citycamp-ai"

    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # City Data Sources
    tulsa_city_council_api_url: str = "https://api.tulsacouncil.org"
    tulsa_city_council_api_key: Optional[str] = None

    # Email
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_tls: bool = True
    smtp_ssl: bool = False
    from_email: Optional[str] = None

    # Application
    project_name: str = "CityCamp AI"
    project_description: str = "CityCamp AI Backend API"
    project_version: str = "1.0.0"
    api_version: str = "v1"
    environment: str = "development"
    debug: bool = True
    cors_origins: List[str] = ["*"]

    # RAG Configuration
    enable_rag: bool = True
    max_tokens: int = 4000
    temperature: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI API key is properly configured"""
        return (
            self.openai_api_key is not None
            and self.openai_api_key.strip() != ""
            and not self.openai_api_key.startswith("sk-placeholder")
        )


settings = Settings()


def get_settings() -> Settings:
    """Get settings instance for dependency injection"""
    return settings
