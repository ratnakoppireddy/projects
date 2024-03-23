from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from common import logger
import uvicorn
from datetime import datetime

DEFAULT_CREDIT_LIMIT = 2000

app = FastAPI()

client = MongoClient('mongodb://localhost:27017/')
db = client['paylater']
user_collection = db['users']
merchant_collection = db['merchants']
transactions_collection = db['transactions']
repayments_collection = db['repayments']


@app.get("/")
async def homepage():
    return {"Hi":"welcome to mongodb paylater"}


class UserCreate(BaseModel):
    name: str
    email: str



@app.put("/newUser")
async def new_user(user: UserCreate):
    try:
        user_collection.insert_one(user.dict())
        msg = "User added successfully!"
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    else:
        return {"message": msg}


class MerchantCreate(BaseModel):
    name: str
    email: str
    fee: float


@app.put("/newMerchant")
async def new_merchant(merchant: MerchantCreate):
    try:
        merchant_collection.insert_one(merchant.dict())
        msg = "Merchant added successfully!"
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
    else:
        return {"message": msg}


class TransactionCreate(BaseModel):
    u_id: int
    m_id: int
    amount: int


@app.put("/transact")
async def transact(transaction: TransactionCreate):
    try:
        user = user_collection.find_one({"user_id": transaction.u_id})
        balance = user['balance']

        merchant = merchant_collection.find_one({"merchant_id": transaction.m_id})
        m_fee = merchant['fee']

        if balance >= transaction.amount:
            formatted_date = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            transactions_collection.insert_one({
                "u_id": transaction.u_id,
                "m_id": transaction.m_id,
                "m_fee": m_fee,
                "t_date": formatted_date,
                "amount": transaction.amount
            })

            user_collection.update_one({"user_id": transaction.u_id}, {"$set": {"balance": balance - transaction.amount}})
            msg = "Transaction successfully updated!"
        else:
            raise HTTPException(status_code=400, detail="Insufficient balance")

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

    return {"message": msg}


@app.get("/getUser/{uid}")
async def get_user(uid: int):
    user = user_collection.find_one({"user_id": uid})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.get("/getMerchant/{mid}")
async def get_merchant(mid: int):
    merchant = merchant_collection.find_one({"merchant_id": mid})
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    return merchant
