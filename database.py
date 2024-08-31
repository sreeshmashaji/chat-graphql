
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
# from dotenv import dotenv_values

# env = dict(dotenv_values(".env_admin"))

mongo_db_uri = "mongodb+srv://sreeshma3023:Sreeshma123#@cluster0.q9pfcac.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
print(mongo_db_uri)

uri = mongo_db_uri

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')

    print(f"Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


db = client.Graph

async def get_database():
    yield db
