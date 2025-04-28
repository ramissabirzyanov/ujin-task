from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DATA_FROM_CBR: str = 'https://www.cbr-xml-daily.ru/daily_json.js'
    TRUE_VALUE: tuple = ('1', 'true', 'y')
    FALSE_VALUE: tuple = ('0', 'false', 'n')

    class Config:
        extra = "allow"


settings = Settings()
