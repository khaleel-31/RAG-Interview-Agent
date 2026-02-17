import os


class Config:
    def __init__(self, huggingface_token=None, groq_api_key=None):
        self.huggingface_token = huggingface_token
        self.groq_api_key = groq_api_key


def get_config():
    """Simple centralized config object for tokens and keys."""
    return Config(
        huggingface_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
    )
