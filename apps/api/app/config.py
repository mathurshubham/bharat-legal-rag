from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    openrouter_api_key: str = ""
    cf_account_id: str = ""
    cf_gateway_id: str = ""
    gen_model: str = "anthropic/claude-sonnet-4-5"
    embed_model: str = "baai/bge-m3"
    reranker_model: str = "nvidia/llama-nemotron-rerank-vl-1b-v2:free"
    hyde_model: str = "openai/gpt-4.1-mini"
    embed_batch_size: int = 64
    cors_origins: str = "http://localhost:3002"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
