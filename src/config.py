import os
from pydantic_settings import BaseSettings, SettingsConfigDict

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
APPDIR = os.path.abspath(os.path.dirname(__file__))


class AppSettings(BaseSettings):
    APP_ENV: str
    APP_NAME: str
    DEBUG: bool
    RELOAD: bool

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASEDIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


class ProductionConfig(AppSettings):
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///" + os.path.join(
        APPDIR, "database", "db", "production.db"
    )
    DEBUG: bool = False
    RELOAD: bool = False
    APP_NAME: str = "Employee Time Tracking API (Production)"


class DevelopmentConfig(AppSettings):
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///" + os.path.join(
        APPDIR, "database", "db", "development.db"
    )
    DEBUG: bool = True
    RELOAD: bool = True
    APP_NAME: str = "Employee Time Tracking API (Development)"


class TestingConfig(AppSettings):
    SQLALCHEMY_DATABASE_URI: str = "sqlite+aiosqlite:///" + os.path.join(
        APPDIR, "database", "db", "test.db"
    )
    DEBUG: bool = True
    RELOAD: bool = True
    APP_NAME: str = "Employee Time Tracking API (Testing)"


config_setting = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

choose_setting = os.getenv("APP_ENV", "development")
SET_CONF = config_setting[choose_setting]()


if __name__ == "__main__":
    print(f"{BASEDIR=}")
    print(f"{APPDIR=}")
    print(SET_CONF)
