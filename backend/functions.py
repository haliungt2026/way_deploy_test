import requests
import json
import pandas as pd
from datetime import datetime
import ast
import operator
import re

def mongol_bank_khansh(date: str) -> pd.DataFrame:
    # 1. Validate date format (YYYY-MM-DD)
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Invalid date format. Expected YYYY-MM-DD")

    url = f"https://www.mongolbank.mn/mn/currency-rates/data?startDate={date}&endDate={date}"

    try:
        response = requests.post(url)
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Request failed: {e}")

    # 2. Check status code
    if 400 <= response.status_code < 500:
        raise Exception(f"Client error ({response.status_code}): Check request parameters")
    elif 500 <= response.status_code < 600:
        raise Exception(f"Server error ({response.status_code}): MongolBank API issue")

    if response.status_code != 200:
        raise Exception(f"Unexpected status code: {response.status_code}")

    # 3. Validate JSON response
    try:
        data = response.json()
    except ValueError:
        return "API дуудхад алдаа гарлаа, хөгжүүлэгчтэй холбогдоорой"

    if not data.get("success", False):
        return "API дуудхад алдаа гарлаа. Түр хүлээгээд дахиад асуугаарай"

    if "data" not in data:
        return "Тухайн өдрийн ханшийн мэдээлэл байхгүй байна"

    return pd.DataFrame(data["data"])



OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg
}

def eval_expr(expr: str):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in OPS:
                return "Unsupported operator"
            return OPS[type(node.op)](_eval(node.left), _eval(node.right))
        
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in OPS:
                return "Unsupported unary operator"
            return OPS[type(node.op)](_eval(node.operand))
        
        else:
            return "Unsupported expression"

    try:
        parsed = ast.parse(expr, mode='eval')
        result = _eval(parsed.body)

        # Хэрвээ дотор нь алдаа string буцсан бол дамжуулна
        if isinstance(result, str):
            return result

        return result

    except ZeroDivisionError:
        return "Division by zero"
    except Exception:
        return "Invalid expression"



def handle_user_query(user_query: str):
    if not isinstance(user_query, str):
        return "Invalid input"

    query = user_query.strip()
    query_lower = query.lower()

    # 1. Contact шалгах
    if any(word in query_lower for word in ["утас", "contact", "холбоо барих", "holbodgoh medeelel"]):
        return "Манай холбоо барих утасны дугаар: 99887766"

    # 2. Location шалгах
    if any(word in query_lower for word in ["байршил", "location"]):
        return "Манай байршил: Galaxy tower 7 давхар, 705 тоот"

    # 3. Date format шалгах (YYYY-MM-DD)
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if re.match(date_pattern, query):
        try:
            return mongol_bank_khansh(query)
        except Exception as e:
            return str(e)

    # 4. Math expression гэж үзэх оролдлого
    # (зөвхөн math тэмдэгтүүд байгаа эсэхийг шалгана)
    math_pattern = r"^[\d+\-*/().\s^]+$"
    if re.match(math_pattern, query):
        try:
            return eval_expr(query)
        except Exception as e:
            return str(e)

    # 5. Default → 그대로 буцаана
    return user_query

