from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mysql.connector import connection
from common import logger
from datetime import datetime
import pytz

DEFAULT_CREDIT_LIMIT = 2000

app = FastAPI()
@app.get("/")
async def homepage():
    return {"test":"Hi"}


def create_connection():
    return connection.MySQLConnection(
        host="127.0.0.1", user="ratna", password="Maurya123", database="paylater"
    )


class UserCreate(BaseModel):
    name: str
    email: str
    balance: int


# creating new user
@app.put("/newUser")
async def new_user(user: UserCreate):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        # conn.autocommit = True # optional
        cursor = conn.cursor()
        query = f"INSERT INTO user (name, email, balance) VALUES ('{user.name}', '{user.email}', {user.balance})"
        cursor.execute(query)
        conn.commit()
        msg = "User added successfully!"
        logger.info(msg)
        response_msg["message"] = msg
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(response_msg["message"])
    else:
        cursor.close()
        conn.close()

    return response_msg


class MerchantCreate(BaseModel):
    name: str
    email: str
    fee: float


# Creating new merchant
@app.put("/newMerchant")
def new_merchant(merchant: MerchantCreate):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"INSERT INTO merchant (name, email, fee) VALUES ('{merchant.name}', '{merchant.email}', {merchant.fee})"
        cursor.execute(query)
        conn.commit()
        msg = "User added successfully!"
        logger.info(msg)
        response_msg["messgage"] = msg
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()
    return response_msg


class TransactionCreate(BaseModel):
    u_id: int
    m_id: int
    amount: int


# creating new transaction
@app.put("/transact")
async def transact(transaction: TransactionCreate):
    response_msg = {
    "status": "success",
    "data": None,
    "message": None
    }
    try:
        conn = create_connection()
        cursor = conn.cursor()

        query = f"SELECT balance FROM user WHERE user_id={transaction.u_id}"
        cursor.execute(query)
        balance = float(cursor.fetchone()[0])

        query2 = f"Select fee from merchant where merchant_id={transaction.m_id}"
        cursor.execute(query2)
        m_fee = float(cursor.fetchone()[0])

        if balance >= transaction.amount:
            _date = datetime.utcnow()
            formatted_date = _date.strftime("%Y-%m-%d %H:%M:%S")

            query = f"INSERT INTO transactions (u_id, m_id, m_fee, t_date, amount) VALUES ({transaction.u_id}, {transaction.m_id},{m_fee}, '{formatted_date}', {transaction.amount})"
            cursor.execute(query)

            query = f"UPDATE user SET balance={balance - transaction.amount} WHERE user_id={transaction.u_id}"
            cursor.execute(query)
            conn.commit()
            msg = "Transaction successfully updated!"
        else:
            response_msg["status"] = "failed"
            msg = "Insufficient balance"
            
        response_msg["message"] = msg
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()
    return response_msg

@app.get("/getUser/{uid}")
async def get_user(uid: int):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute(f"SELECT * FROM user WHERE user_id={uid}")
        response_msg["data"] = cursor.fetchall()
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()

    return response_msg  # internally serialized inti JSON


@app.get("/getMerchant/{mid}")
async def get_merchant(mid: int):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor(buffered=True, dictionary=True)
        cursor.execute(f"SELECT * FROM merchant WHERE merchant_id={mid}")
        response_msg["data"] = cursor.fetchall()
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()
    return response_msg


class UpdateFeeModel(BaseModel):
    mid: int
    fee: float


@app.post("/updateFee")
async def update_fee(uData: UpdateFeeModel):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"UPDATE merchant SET fee={uData.fee} WHERE merchant_id={uData.mid}"
        cursor.execute(query)
        conn.commit()
        msg = "Merchant fee updated successfully!"
        response_msg["message"] = msg
        logger.info(msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()

    return response_msg


class repayment(BaseModel):
    uid: int
    amount: int


@app.post("/repay")
async def repay(repay: repayment):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT balance FROM user WHERE user_id='{repay.uid}'"
        cursor.execute(query)
        balance = float(cursor.fetchone()[0])
        due = DEFAULT_CREDIT_LIMIT - balance
        if due >= repay.amount:
             _date = datetime.utcnow()
             formatted_date = _date.strftime("%Y-%m-%d %H:%M:%S")
             query = f"UPDATE user SET balance={balance + repay.amount} WHERE user_id={repay.uid}"
             cursor.execute(query)
             conn.commit()
             msg = "Repayment successful!"
             query = f"INSERT into repayments (u_id,amount,repay_date) values ({repay.uid},{repay.amount},'{formatted_date}')"
             cursor.execute(query)
             conn.commit()
        else:
             response_msg["status"] = "failed"
             msg = f"You cannot pay more than {due} amount!"

        response_msg["message"] = msg
        logger.info(msg)
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()

    return response_msg


# class FeeCollected


@app.get("/feeCollected/{merchant}")
async def get_merchant_fee(merchant: str):
    response_msg = {"status": "success", "data": None, "message": None}
    try:
        conn = create_connection()
        cursor = conn.cursor()
        query = f"SELECT SUM(amount*m_fee/100) FROM transactions WHERE m_id={merchant}"
        cursor.execute(query)
        fee_collected = cursor.fetchone()
        response_msg["data"] = fee_collected
        logger.info(f"Fee collected for {merchant} is {fee_collected}")
    except Exception as ex:
        response_msg["status"] = "failed"
        response_msg["message"] = str(ex)
        logger.error(str(ex))
    else:
        cursor.close()
        conn.close()

    return response_msg


# Reporting


@app.get("/dues/{u_id}")
async def get_user_dues(u_id: str):
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT balance FROM user WHERE user_id={u_id}"
    cursor.execute(query)
    dues = DEFAULT_CREDIT_LIMIT - float(cursor.fetchone()[0])
    cursor.close()
    conn.close()
    return {"dues": dues}


@app.get("/usersAtLimit")
async def get_users_at_limit():
    conn = create_connection()
    cursor = conn.cursor()
    query = f"SELECT name FROM user WHERE balance={DEFAULT_CREDIT_LIMIT}"
    cursor.execute(query)
    users = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return {"users": users}


@app.get("/totalDues")
async def get_total_dues():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT COUNT(*), SUM(balance) FROM user"
    cursor.execute(query)
    data = cursor.fetchone()
    user_count, total_balance = data[0], float(data[1])
    total_dues = (user_count * DEFAULT_CREDIT_LIMIT) - total_balance
    cursor.close()
    conn.close()
    return {"total_dues": total_dues}


@app.get("/creditReached")
async def get_total_dues():
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT name FROM user WHERE balance=0.0"
    cursor.execute(query)
    names = [name[0] for name in cursor]
    cursor.close()
    conn.close()
    return {"names":names}
