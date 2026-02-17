"""
Configuration Settings for InsightHub API

This module contains all configuration variables for the application.
"""
import os
from typing import Optional

# Database Configuration
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Akashbalasu064!@localhost:5432/eventhub"
)

# API Configuration
API_TITLE: str = "InsightHub"
API_VERSION: str = "1.0.0"
API_DESCRIPTION: str = "Real-time Event Ingestion & Analytics Platform"

# CORS Configuration
CORS_ORIGINS: list = ["*"]  # Tighten in production

# Application Settings
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
