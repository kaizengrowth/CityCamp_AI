from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost/citycamp_db"
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "citycamp_db"
    database_user: str = "user"
    database_password: str = "password"

    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # External APIs
    openai_api_key: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None

    # AWS
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: Optional[str] = None

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # City Data Sources
    tulsa_city_council_api_url: Optional[str] = None
    tulsa_city_council_api_key: Optional[str] = None

    # Application
    environment: str = "development"
    debug: bool = True
    api_version: str = "v1"
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
    ]

    # Project info
    project_name: str = "CityCamp AI"
    project_description: str = "Tulsa Civic Engagement Platform"
    project_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
