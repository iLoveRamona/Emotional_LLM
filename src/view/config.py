import dotenv
import os
dotenv.load_dotenv(dotenv.find_dotenv())
model_uri = os.getenv('MODEL_URI')
api_key = os.getenv('API')