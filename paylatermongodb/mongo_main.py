from fastapi import FastAPI, HTTPException
#from pydantic import BaseModel
#from pymongo import MongoClient
from bson import ObjectId
from common import logger
import uvicorn
from datetime import datetime,timezone
from connection import users_collection,merchants_collection,transactions_collection,repayments_collection
from classes import User,Merchant,Transaction,Repayment,UpdateFee
DEFAULT_CREDIT_LIMIT = 2000

app = FastAPI()




@app.get("/")
async def home_page():
    return {"Hi": "Welcome to Paylater"}

# class get(BaseModel):
#        name:str
# @app.get("/getuser/")
# def get_user(un:get):




#to create a new user
@app.post("/newUser/")
def new_user(user: User):
    response_msg = {"status": "success", "data": None, "message": None}

    query = {"name":user.name,"email":user.email,"balance":DEFAULT_CREDIT_LIMIT}
    try:
        result = users_collection.insert_one(query)
        response_msg["message"] = "User added successfully!"
        logger.info("User added successfully!")
    
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))

    return response_msg

#to create a new merchant 


@app.put("/newMerchant")
def new_merchant(merchant: Merchant):
    response_msg = {"status": "success", "data": None, "message": None}
    query = {"name":merchant.name,"email":merchant.email,"fee":merchant.fee}

    try:
        result = merchants_collection.insert_one(query)
        response_msg["message"]= "Merchant added successfully!"
        logger.info("Merchant added successfully!")

    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)

    return response_msg


# to do a transaction


@app.put("/transact")
def transact(transaction: Transaction):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        balance_dict= users_collection.find_one({"_id": ObjectId(transaction.u_id)})
        balance_dict['id'] = str(balance_dict['_id'])
        del[balance_dict['_id']]
        bal = balance_dict["balance"]

        m_fee_dict = merchants_collection.find_one({"_id": ObjectId(transaction.m_id)})
        m_fee_dict['id'] = str(m_fee_dict['_id'])
        del[m_fee_dict['_id']]
        m_fee = m_fee_dict['fee']

        _date = datetime.now(timezone.utc)
        formatted_date = _date.strftime("%Y-%m-%d %H:%M:%S")

        if bal >= transaction.amount:
            transaction_doc = {
                "u_id": ObjectId(transaction.u_id),
                "m_id": ObjectId(transaction.m_id),
                "m_fee": m_fee,
                "t_date": formatted_date, 
                "amount": transaction.amount}
            
            transactions_collection.insert_one(transaction_doc)
            
            users_collection.update_one({"_id": ObjectId(transaction.u_id)}, {"$inc": {"balance": -transaction.amount}})
            response_msg["message"] = "Transaction successfully updated!"
              
        else:
            response_msg["status"]= "failed"
            response_msg["message"]= "Insufficient balance"
        
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)

    return response_msg


# to pay due amount


@app.post("/repay/")
async def repay(rpay:Repayment):
    response_msg = {"status": "success","data": None, "message": None }
    try:
        balance_dict= users_collection.find_one({"_id": ObjectId(rpay.u_id)})
        balance_dict['id'] = str(balance_dict['_id'])
        del[balance_dict['_id']]
        bal = balance_dict["balance"]
        
        due = DEFAULT_CREDIT_LIMIT - bal
        
        _date = datetime.now(timezone.utc)
        formatted_date = _date.strftime("%Y-%m-%d %H:%M:%S")
        
        if due >= rpay.amount:
            rpay_doc = {
                "u_id": ObjectId(rpay.u_id),
                "t_date": formatted_date, 
                "amount": rpay.amount}
            
            repayments_collection.insert_one(rpay_doc)
            
            users_collection.update_one({"_id": ObjectId(rpay.u_id)}, {"$inc": {"balance": rpay.amount}})
            response_msg["message"] = "Repayment successfully updated!"

        else:
            response_msg["status"]= "failed"
            response_msg["message"]= "You cannot pay more than {due} amount!"
        
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)

    return response_msg


# to update merchant fee


@app.post("/updateFee/")
async def update_fee(uData: UpdateFee):
    response_msg = {"status": "success","data": None,"message": None}
    try:
        merchants_collection.update_one({"_id": ObjectId(uData.mid)}, {"$set": {"fee": uData.fee}})
        msg ="Merchant fee updated successfully!"
        response_msg["message"] =  msg
        logger.info(msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    return response_msg

# total fee collected a merchant
@app.get("/feeCollected/{merchant}")
async def get_merchant_fee(merchant: str):
    response_msg = {"status": "success","data": None,"message": None}
    try:
        pipeline = [
            {"$match": {"m_id": ObjectId(merchant)}},
            {"$group": {"_id": None, "total_fee": {"$sum": {"$multiply": ["$amount", {"$divide": ["$m_fee", 100]}]}}}}
        ]
        fee_collected = list(transactions_collection.aggregate(pipeline))
        response_msg["data"] = fee_collected[0]['total_fee'] if fee_collected else 0
        logger.info(f"Fee collected for {merchant} is {response_msg['data']}")

    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))

    return response_msg


# to get a user details
@app.get("/getUser/{uid}")
async def get_user(uid: str):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        user = users_collection.find_one({"_id": ObjectId(uid)})
        user['id'] = str(user['_id'])
        del[user['_id']]
        if user:
            logger.info("User added successfully!")
            response_msg["data"]= user
            response_msg["message"]= "User found"
        else:
            logger.info("User not found")
            response_msg["status"]= "failed"
            response_msg["message"]= "User not found"
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
    return response_msg


# to get merchant details
@app.get("/getmerchant/{mid}")
async def get_merchant(mid: str):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        merchant = merchants_collection.find_one({"_id": ObjectId(mid)})
        merchant['id'] = str(merchant['_id'])
        del[merchant['_id']]
        if merchant:
            logger.info("Merchant added successfully!")
            response_msg["data"]= merchant
            response_msg["message"]= "merchant found"
        else:
            logger.info("Merchant not found")
            response_msg["status"]= "failed"
            response_msg["message"]= "Merchant not found"
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
    return response_msg


# Reporting

# to get user due amount 
@app.get("/dues/{u_id}")
def get_user_dues(u_id: str):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        user = users_collection.find_one({"_id": ObjectId(u_id)})
        bal = user["balance"] 
        dues = DEFAULT_CREDIT_LIMIT - bal
        logger.info("Due omount of user {u_id} is {dues}")
        response_msg["data"]= dues
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
    return response_msg

# to get users list have not used thier credit limit
@app.get("/usersAtLimit")
def get_users_at_limit():
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        users_list = users_collection.find({ "balance": DEFAULT_CREDIT_LIMIT }, { "name": 1, "_id": 0 })
        users_names = [user["name"] for user in users_list]
        logger.info("Users at limit is/are {users_names}")
        response_msg["data"]= users_names
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
    return response_msg

# total dues from all users
@app.get("/totalDues")
async def get_total_dues():
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        pipeline = [{"$group": {"_id": None,"count": {"$sum": 1},"total_balance": {"$sum": "$balance"} }}]

        result = list(users_collection.aggregate(pipeline))
        if result:
            user_count = result[0]["count"]
            total_balance = result[0]["total_balance"]
            total_dues = (user_count * DEFAULT_CREDIT_LIMIT) - total_balance
            return {"total_dues": total_dues}
        else:
            return {"total_dues": 0} 
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
        return response_msg

# user who reached their credit limit
@app.get("/creditReached")
async def get_total_dues():
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        users_list = users_collection.find({ "balance": 0.0 }, { "name": 1, "_id": 0 })
        users_names = [user["name"] for user in users_list]
        logger.info("Users at limit is/are {users_names}")
        response_msg["data"]= users_names
    except Exception as ex:
        logger.error(str(ex))
        response_msg["status"]= "failed"
        response_msg["message"]= str(ex)
    return response_msg


if __name__ == "__main__":
    uvicorn.run("mongo_main:app", host="0.0.0.0", port=8000,reload=True)