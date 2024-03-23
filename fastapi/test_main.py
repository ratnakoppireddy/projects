import requests
import json
from mysql.connector import connection


def test_get_employeeby_id_not_found():
    url = "http://0.0.0.0:8000/getEmployeeById/8888"

    payload = {}
    headers = {}

    response = requests.get(url, headers=headers, data=payload)
    res = response.json()
    assert res["status"] == "failed"
    assert res["message"] == "Employee Not Found!"


def test_get_employee_by_id():
    url = "http://0.0.0.0:8000/getEmployeeById/1501"

    payload = {}
    headers = {}

    response = requests.get(url, headers=headers, data=payload)
    res = response.json()

    assert res[0]["firstName"] == "Larry"
    assert res[0]["lastName"] == "Bott"
    assert res[0]["email"] == "lbott@classicmodelcars.com"


def test_add_employee():
    try:
        conn = connection.MySQLConnection(
            user="ratna",
            password="Maurya123",
            host="127.0.0.1",
            database="classicmodels",
        )
        print("Database hasbeen connected succesfully!")
    except Exception as ex:
        print(f"Database connectivity failed! error: {ex}")
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM employees WHERE employeeNumber=2244")
        conn.commit()
    except Exception as ex:
        print(f"Database error: {ex}")

    url = "http://0.0.0.0:8000/addEmployee/"
    payload = json.dumps(
        {
            "employeeNumber": 2244,
            "lastName": "Carter",
            "firstName": "jhon",
            "extension": "x2244",
            "email": "jhon@company.com",
            "officeCode": "7",
            "reportTo": 1102,
            "jobTitle": "Sales Rep",
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=payload)
    res = response.json()
    assert res["status"] == "success"

    cur.close()
    conn.close()


if __name__ == "__main__":
    # test_get_employee_by_id()
    # test_get_employeeby_id_not_found()
    pass
