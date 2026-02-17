"""Centralized configuration module."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    huggingface_token: Optional[str] = None
    groq_api_key: Optional[str] = None


def get_config() -> Config:
    """Load configuration from environment variables."""
    return Config(
        huggingface_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
