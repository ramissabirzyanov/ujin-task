from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс для хранения настроек приложения, загружаемых из переменных окружения.
    """
    DATABASE_URL: str = 'https://www.cbr-xml-daily.ru/daily_json.js'

    class Config:
        extra = "allow"

settings = Settings()
