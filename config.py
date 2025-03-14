from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from the .env file

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:@localhost/ckd_platform')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
