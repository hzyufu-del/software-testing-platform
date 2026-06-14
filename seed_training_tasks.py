"""Seed the database with training tasks.

Usage:
    python seed_training_tasks.py
"""

from app import create_app, db
from app.models import TrainingTask

app = create_app()

TASKS = [
    {
        "title": "登录接口测试",
        "description": "测试模拟登录接口，验证用户名密码正确时返回成功，错误时返回失败。",
        "method": "POST",
        "endpoint": "/mock/login",
        "request_example": '{"username": "admin", "password": "123456"}',
        "expected_example": '{"code": 200, "message": "登录成功", "token": "mock-token"}',
        "sort_order": 1,
    },
    {
        "title": "用户查询接口测试",
        "description": "测试用户查询接口，根据用户ID查询用户信息，验证返回数据结构。",
        "method": "GET",
        "endpoint": "/mock/user/1",
        "request_example": "",
        "expected_example": '{"code": 200, "message": "查询成功", "data": {"id": 1, "username": "admin"}}',
        "sort_order": 2,
    },
    {
        "title": "商品添加接口测试",
        "description": "测试商品添加接口，提交商品名称和价格，验证创建成功。注意需要POST请求和JSON参数。",
        "method": "POST",
        "endpoint": "/mock/product/add",
        "request_example": '{"product_name": "测试商品", "price": 99.9}',
        "expected_example": '{"code": 200, "message": "商品添加成功"}',
        "sort_order": 3,
    },
    {
        "title": "参数异常接口测试",
        "description": "测试参数缺失时接口是否正确返回错误。故意不传必要参数，验证错误处理。",
        "method": "POST",
        "endpoint": "/mock/product/add",
        "request_example": '{"product_name": "缺少价格的商品"}',
        "expected_example": '{"code": 400, "message": "参数缺失"}',
        "sort_order": 4,
    },
]


def seed():
    """Insert training tasks into the database."""
    with app.app_context():
        if TrainingTask.query.first() is not None:
            print("实训任务数据已存在，跳过插入。")
            return

        for task_data in TASKS:
            task = TrainingTask(**task_data)
            db.session.add(task)

        db.session.commit()
        print(f"已插入 {len(TASKS)} 个接口实训任务。")


if __name__ == "__main__":
    seed()
