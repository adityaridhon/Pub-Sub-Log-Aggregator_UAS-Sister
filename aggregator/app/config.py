import os


class Settings:

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:pass@storage:5432/logdb"
    )

    REDIS_URL: str = os.getenv(
        "REDIS_URL",
        "redis://broker:6379"
    )


settings = Settings()