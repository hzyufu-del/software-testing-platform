"""Mock API endpoints for interface testing training."""

from flask import Blueprint, jsonify, request

mock_bp = Blueprint("mock", __name__, url_prefix="/mock")


@mock_bp.post("/login")
def mock_login():
    """Mock login endpoint."""
    data = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if username == "admin" and password == "123456":
        return jsonify(code=200, message="登录成功", token="mock-token-abc123")
    return jsonify(code=401, message="用户名或密码错误"), 401


@mock_bp.get("/user/<int:user_id>")
def mock_user(user_id: int):
    """Mock user query endpoint."""
    if user_id == 1:
        return jsonify(code=200, message="查询成功", data={"id": 1, "username": "admin"})
    return jsonify(code=404, message="用户不存在"), 404


@mock_bp.post("/product/add")
def mock_product_add():
    """Mock product add endpoint."""
    data = request.get_json(silent=True) or {}
    product_name = data.get("product_name", "")
    price = data.get("price")

    if not product_name or price is None:
        return jsonify(code=400, message="参数缺失，需要 product_name 和 price"), 400
    return jsonify(
        code=200,
        message="商品添加成功",
        data={"product_name": product_name, "price": price},
    )
