from pymongo import MongoClient


# MongoDB connection
# client = MongoClient('mongodb://{socket.gethostname()}.local:27017/')
client = MongoClient('mongodb://localhost:27017/')
db = client['paylater']
users_collection = db['users']
merchants_collection = db['merchants']
transactions_collection = db['transactions']
repayments_collection = db['repayments']
