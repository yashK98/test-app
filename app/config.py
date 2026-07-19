from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # SQLite by default = zero setup. Swap to Postgres with:
    #   DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db   (and install psycopg)
    database_url: str = "sqlite:///./drift.db"

    # --- Kubernetes access (we shell out to the same binaries you use by hand) ---
    kubectl_bin: str = "kubectl"          # use a full path if it's not on PATH
    skectl_bin: str = "skectl"            # kept for reference / future use

    # Command run to authenticate before talking to the cluster.
    # Leave blank if you authenticate manually in your terminal first.
    # Examples:  "skectl get-token"   /   "skectl login --cluster prod"
    skectl_cmd: str = ""

    # If true, skectl_cmd prints a bearer token on stdout and we pass it to
    # kubectl via --token. If false, we assume running skectl_cmd updates your
    # kubeconfig and plain kubectl calls are then authenticated.
    skectl_token_mode: bool = False

    # Optional: pin a kubeconfig context for every kubectl call
    kubectl_context: str = ""

    # Seconds a fetched token is reused before re-running skectl_cmd (token mode)
    token_ttl: int = 900

    kubectl_timeout: int = 30
    auth_timeout: int = 120


settings = Settings()
