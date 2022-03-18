from pydantic import BaseSettings

# creating data validation for environment variables, easier for troubleshooting
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # referencing environment variables declared in .env file
    class Config:
        env_file = ".env"

# creating an instance of class Settings and store it in a "settings" variable
# can be imported in other modules
settings = Settings()