from pydantic import BaseModel 

#this class is used to validate user details
class User(BaseModel):
    name: str
    email: str

class Merchant(BaseModel):
    name: str
    email: str
    fee: float  

class Transaction(BaseModel):
    u_id: str
    m_id: str
    amount: float     

class Repayment(BaseModel):
    u_id: str
    amount: float     

class UpdateFee(BaseModel):
    mid : str
    fee : float    