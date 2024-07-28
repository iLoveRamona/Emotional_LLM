import dotenv
import os
dotenv.load_dotenv(dotenv.find_dotenv())
model_uri = os.getenv('MODEL_URI')
api = os.getenv('API')