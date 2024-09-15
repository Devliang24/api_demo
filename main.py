from fastapi import FastAPI, HTTPException, Header, status
from pydantic import BaseModel
import uuid
import uvicorn

# 创建 FastAPI 应用实例
app = FastAPI()

# 模拟数据库
# 用户数据库，包含用户名、密码和 token
mock_users_db = {
    "456": {"username": "zhangsan", "password": "123456", "token": ""}
}
# 商品数据库，包含商品 ID、名称和价格
mock_products_db = {
    "101": {"name": "Apple iPhone 13", "price": 799.99},
    "102": {"name": "Dell XPS 13", "price": 999.99}
}
# 购物车数据库，存储购物车项信息
mock_cart_db = {}
# 订单数据库，存储订单信息
mock_orders_db = {}


# 数据模型定义
# 商品数据模型
class Product(BaseModel):
    name: str
    price: float


# 购物车项数据模型
class CartItem(BaseModel):
    product_id: str
    quantity: int


# 创建订单请求数据模型
class OrderRequest(BaseModel):
    cart_id: str


# 更新订单请求数据模型
class UpdateOrderRequest(BaseModel):
    cart_id: str
    quantity: int


# 登录请求数据模型
class LoginRequest(BaseModel):
    username: str
    password: str


# 统一的接口返回格式函数
def response(data=None, message="成功", code=200):
    """
    生成统一格式的接口响应。

    :param data: 响应数据
    :param message: 响应消息
    :param code: 响应状态码
    :return: 包含 code、message 和 data 的字典
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


# 模拟的用户验证函数
def get_current_user(token: str):
    """
    验证用户 token，并返回用户信息。

    :param token: 用户的 token
    :return: 用户信息字典，如果 token 无效则抛出 HTTPException
    """
    for user_id, user in mock_users_db.items():
        if user["token"] == token:
            return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 token")


# 登录接口
@app.post("/login")
async def login(request: LoginRequest):
    """
    用户登录接口，验证用户名和密码，并返回 token。

    :param request: 包含用户名和密码的登录请求对象
    :return: 包含生成的 token 的响应
    """
    for user_id, user in mock_users_db.items():
        if user["username"] == request.username and user["password"] == request.password:
            # 生成新的唯一 token
            user["token"] = str(uuid.uuid4())
            return response({"token": user["token"]})
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")


# 商品管理接口

# 创建商品接口
@app.post("/api/v1/products")
async def create_product(product: Product, authorization: str = Header(...)):
    """
    创建商品接口，新增一个商品。需提供有效的 token。

    :param product: 包含商品名称和价格的商品对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含生成的商品 ID 和商品信息的响应
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    product_id = str(len(mock_products_db) + 101)
    mock_products_db[product_id] = product.dict()
    return response({"product_id": product_id, "product": product})


# 查询所有商品接口
@app.get("/api/v1/products")
async def list_products(authorization: str = Header(...)):
    """
    查询所有商品接口，返回商品列表。需提供有效的 token。

    :param authorization: 包含用户 token 的请求头
    :return: 包含商品列表的响应
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    return response([{"id": pid, **p} for pid, p in mock_products_db.items()])


# 查询单个商品接口
@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: str, authorization: str = Header(...)):
    """
    查询单个商品接口，根据商品 ID 返回商品详情。需提供有效的 token。

    :param product_id: 商品的唯一标识符
    :param authorization: 包含用户 token 的请求头
    :return: 包含商品详情的响应，如果商品未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    product = mock_products_db.get(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品未找到")
    return response({"id": product_id, **product})


# 更新商品接口
@app.put("/api/v1/products/{product_id}")
async def update_product(product_id: str, product: Product, authorization: str = Header(...)):
    """
    更新商品接口，根据商品 ID 更新商品信息。需提供有效的 token。

    :param product_id: 商品的唯一标识符
    :param product: 包含更新后的商品名称和价格的商品对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含更新后的商品 ID 和商品信息的响应，如果商品未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    if product_id not in mock_products_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品未找到")
    mock_products_db[product_id] = product.dict()
    return response({"id": product_id, **product.dict()})


# 删除商品接口
@app.delete("/api/v1/products/{product_id}")
async def delete_product(product_id: str, authorization: str = Header(...)):
    """
    删除商品接口，根据商品 ID 删除商品。需提供有效的 token。

    :param product_id: 商品的唯一标识符
    :param authorization: 包含用户 token 的请求头
    :return: 包含删除消息和被删除商品信息的响应，如果商品未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    if product_id not in mock_products_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品未找到")
    deleted_product = mock_products_db.pop(product_id)
    return response({"message": "商品已删除", "product": deleted_product})


# 购物车管理接口

# 添加购物车项接口
@app.post("/api/v1/cart")
async def add_to_cart(cart_item: CartItem, authorization: str = Header(...)):
    """
    添加购物车项接口，添加一个商品到购物车。需提供有效的 token。

    :param cart_item: 包含商品 ID 和数量的购物车项对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含生成的购物车 ID 和购物车项信息的响应
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    cart_id = str(len(mock_cart_db) + 1)
    mock_cart_db[cart_id] = cart_item.dict()
    return response({"cart_id": cart_id, "cart_item": cart_item})


# 查询购物车接口
@app.get("/api/v1/cart")
async def list_cart_items(authorization: str = Header(...)):
    """
    查询购物车接口，返回购物车中的所有商品。需提供有效的 token。

    :param authorization: 包含用户 token 的请求头
    :return: 包含购物车项列表的响应
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    return response([{"id": cid, **item} for cid, item in mock_cart_db.items()])


# 更新购物车项接口
@app.put("/api/v1/cart/{cart_id}")
async def update_cart_item(cart_id: str, cart_item: CartItem, authorization: str = Header(...)):
    """
    更新购物车项接口，根据购物车项 ID 更新商品信息。需提供有效的 token。

    :param cart_id: 购物车项的唯一标识符
    :param cart_item: 包含更新后的商品 ID 和数量的购物车项对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含更新后的购物车项 ID 和购物车项信息的响应，如果购物车项未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    if cart_id not in mock_cart_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项未找到")
    mock_cart_db[cart_id] = cart_item.dict()
    return response({"id": cart_id, **cart_item.dict()})


# 删除购物车项接口
@app.delete("/api/v1/cart/{cart_id}")
async def delete_cart_item(cart_id: str, authorization: str = Header(...)):
    """
    删除购物车项接口，根据购物车项 ID 删除商品。需提供有效的 token。

    :param cart_id: 购物车项的唯一标识符
    :param authorization: 包含用户 token 的请求头
    :return: 包含删除消息和被删除购物车项信息的响应，如果购物车项未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    if cart_id not in mock_cart_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项未找到")
    deleted_item = mock_cart_db.pop(cart_id)
    return response({"message": "购物车项已删除", "cart_item": deleted_item})


# 订单管理接口

# 创建订单接口
@app.post("/api/v1/orders")
async def create_order(request: OrderRequest, authorization: str = Header(...)):
    """
    创建订单接口，根据购物车项 ID 创建订单。需提供有效的 token。

    :param request: 包含购物车 ID 的创建订单请求对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含生成的订单 ID 和总价的响应，如果购物车项或商品未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)

    cart_item = mock_cart_db.get(request.cart_id)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项未找到")

    product = mock_products_db.get(cart_item["product_id"])
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品未找到")

    order_id = str(len(mock_orders_db) + 1)
    mock_orders_db[order_id] = {
        "product": product,
        "quantity": cart_item["quantity"],
        "total_price": product["price"] * cart_item["quantity"]
    }

    # 下单后移除购物车中的对应项
    # mock_cart_db.pop(request.cart_id)

    return response({"order_id": order_id, "total_price": product["price"] * cart_item["quantity"]})


# 查询所有订单接口
@app.get("/api/v1/orders")
async def list_orders(authorization: str = Header(...)):
    """
    查询所有订单接口，返回所有订单信息。需提供有效的 token。

    :param authorization: 包含用户 token 的请求头
    :return: 包含订单列表的响应
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    return response([{"id": oid, **order} for oid, order in mock_orders_db.items()])


# 查询单个订单接口
@app.get("/api/v1/orders/{order_id}")
async def get_order(order_id: str, authorization: str = Header(...)):
    """
    查询单个订单接口，根据订单 ID 返回订单详情。需提供有效的 token。

    :param order_id: 订单的唯一标识符
    :param authorization: 包含用户 token 的请求头
    :return: 包含订单详情的响应，如果订单未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)
    order = mock_orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")
    return response({"id": order_id, **order})


# 更新订单接口
@app.put("/api/v1/orders/{order_id}")
async def update_order(order_id: str, request: UpdateOrderRequest, authorization: str = Header(...)):
    """
    更新订单接口，根据订单 ID 更新订单信息。需提供有效的 token。

    :param order_id: 订单的唯一标识符
    :param request: 包含购物车 ID 和数量的更新订单请求对象
    :param authorization: 包含用户 token 的请求头
    :return: 包含更新后的订单 ID 和订单信息的响应，如果订单、购物车项或商品未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)

    print(f"Received cart_id: {request.cart_id}")
    print(f"Mock Cart DB: {mock_cart_db}")

    if order_id not in mock_orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")

    cart_item = mock_cart_db.get(request.cart_id)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="购物车项未找到")

    product = mock_products_db.get(cart_item["product_id"])
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="商品未找到")

    mock_orders_db[order_id] = {
        "product": product,
        "quantity": request.quantity,
        "total_price": product["price"] * request.quantity
    }

    return response({"id": order_id, "order": mock_orders_db[order_id]})


# 删除订单接口
@app.delete("/api/v1/orders/{order_id}")
async def delete_order(order_id: str, authorization: str = Header(...)):
    """
    删除订单接口，根据订单 ID 删除订单。需提供有效的 token。

    :param order_id: 订单的唯一标识符
    :param authorization: 包含用户 token 的请求头
    :return: 包含删除消息和被删除订单信息的响应，如果订单未找到则抛出 HTTPException
    """
    token = authorization.split(" ")[1]
    get_current_user(token)

    if order_id not in mock_orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="订单未找到")

    deleted_order = mock_orders_db.pop(order_id)
    return response({"message": "订单已删除", "order": deleted_order})

#if __name__ == "__main__":
#    # 运行 FastAPI 应用
#    uvicorn.run(app, host="0.0.0.0", port=8000)