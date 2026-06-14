from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    POLICY_FILE_PATH: str = "./policy_terms.json"
    TEST_CASES_PATH: str = "./test_cases.json"
    LOG_LEVEL: str = "INFO"
    PLUM_EVAL_MODE: str = "false"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
