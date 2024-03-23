from fastapi import FastAPI
from mysql.connector import connection
from enum import Enum
from pydantic import BaseModel, EmailStr, ValidationError
from typing import Any
import uvicorn
from common import log


class Employee(BaseModel):
    employeeNumber: int
    lastName: str | None = None
    firstName: str
    extension: str | None = None
    email: str | EmailStr = "default@company.com"
    officeCode: str | None = None
    reportTo: int | None = None
    jobTitle: str | None = None


try:
    conn = connection.MySQLConnection(
        user="ratna", password="Maurya123", host="127.0.0.1", database="classicmodels"
    )
    log.info("Database hasbeen connected succesfully!")
except Exception as ex:
    log.error(f"Database connectivity failed! error: {ex}")

cursor = conn.cursor(dictionary=True)

app = FastAPI()


class Designation(str, Enum):
    salesRep = ("Sales Rep",)
    mgrSales = ("Mgr Sales",)
    president = "President"


@app.get("/")
async def home():
    return {"message": "Hello Naren"}


# Type hints as Return
# 1. if all attributes of Pydantic model must be matching with all keys of dict
# 2. return type must be of Pydantic Objects


# type hints as response_model
# Atleast mandatory  of PyDantic model must me provided as dict keys


@app.get("/getEmployees", response_model=list[Employee] | dict)
async def get_employees():
    try:
        cursor.execute("select employeeNumber, firstName from employees limit 10")
         
        data = [rec for rec in cursor]  # list[dicts]
        log.info("Data being returned..")
        return data

    except Exception as ex:
        log.error(f"Cannot get the data {ex}")
        return {"status": "failed", "error": str(ex)}


@app.get("/getEmployeeById/{emp_id}")
async def get_employee_by_id(emp_id) -> list[Employee] | dict:
    try:
        cursor.execute(f"SELECT * FROM employees WHERE employeeNumber={emp_id}")
        all_data = cursor.fetchall()
        if all_data:
            data = [Employee(**rec) for rec in all_data]  # list[Employee]
            return data
        else:
            log.info(f"Could not find employee with id {emp_id}")
            return {"status": "failed", "message": "Employee Not Found!"}

    except Exception as ex:
        log.error(f"Cannot get the data {ex}")
        return {"status": "failed", "error": str(ex)}


@app.get("/getEmployeeByDsgn/{dsgn}")
async def get_employee_by_dsgn(dsgn: Designation):
    try:
        cursor.execute(f"SELECT * FROM employees WHERE jobTitle='{dsgn.value}'")
        all_data = cursor.fetchall()
        if all_data:
            data = [Employee(**rec) for rec in all_data]
            return data
        else:
            log.info(f"could not find employee details with {dsgn}")
            return {"status":"failed","message":"Employee not found by designation"}

    except Exception as ex:
        log.error(f"Cannot get the data {ex}")
        return {"status": "failed", "error": str(ex)}




@app.get("/getEmployeeRange/}")
async def get_employee_by_range(start: int = 1088, end: int = 1337):
        try:
           cursor.execute(
           f"SELECT * FROM employees WHERE employeeNumber BETWEEN {start} AND {end}")
           data = [rec for rec in cursor]
           log.info(f"Data Retrived")
           return {"message": "sucess", "data": data}
        except Exception as ex:
           log.error(f"Cannot get the data {ex}")
           return {"status": "failed", "error": str(ex)}
   




@app.post("/addEmployee/")
async def add_employee(emp: Employee) -> dict:
    try:
        cursor.execute(
            f"""INSERT INTO employees(employeeNumber, lastName, firstName, extension, email, officeCode, reportsTo,jobTitle)
                VALUES ({emp.employeeNumber}, '{emp.lastName}', '{emp.firstName}', '{emp.extension}', '{emp.email}', '{emp.officeCode}', {emp.reportTo}, '{emp.jobTitle}')"""
        )
        conn.commit()
        log.info("Record inserted successfully!")
        return {
            "status": "success",
            "message": "Record has been successfully inserted!",
        }

    except Exception as ex:
        log.error(str(ex))
        return {"status": "failed", "message": str(ex)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
