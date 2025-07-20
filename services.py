from fastapi import HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import List, Optional

from database import get_database
from models import (
    ProductCreate, Product, ProductResponse, ProductCreateResponse,
    OrderCreate, Order, OrderCreateResponse, OrderResponse, 
    ProductsListResponse, OrdersListResponse, PageInfo,
    OrderItemResponse, ProductDetails
)


class ProductService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.products

    async def create_product(self, product: ProductCreate) -> ProductCreateResponse:
        """Create a new product"""
        product_dict = product.model_dump()
        result = await self.collection.insert_one(product_dict)
        return ProductCreateResponse(id=str(result.inserted_id))

    async def get_products(
        self, 
        name: Optional[str] = None, 
        size: Optional[str] = None, 
        limit: int = 10, 
        offset: int = 0
    ) -> ProductsListResponse:
        """Get products with filtering and pagination"""
        query = {}
        
        # Name filter with regex support
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        
        # Size filter
        if size:
            query["size.size"] = size
        
        # Count total documents for pagination
        total_count = await self.collection.count_documents(query)
        
        # Get products with pagination
        cursor = self.collection.find(query).skip(offset).limit(limit)
        products = []
        
        async for product in cursor:
            products.append(ProductResponse(
                id=str(product["_id"]),
                name=product["name"],
                price=product["price"]
            ))
        
        # Calculate pagination info
        next_offset = offset + limit if offset + limit < total_count else None
        previous_offset = max(0, offset - limit) if offset > 0 else None
        
        page_info = PageInfo(
            next=next_offset,
            limit=len(products),
            previous=previous_offset
        )
        
        return ProductsListResponse(data=products, page=page_info)

    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        if not ObjectId.is_valid(product_id):
            return None
        
        product = await self.collection.find_one({"_id": ObjectId(product_id)})
        if product:
            return Product(**product)
        return None


class OrderService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.orders
        self.product_service = ProductService(db)

    async def create_order(self, order: OrderCreate) -> OrderCreateResponse:
        """Create a new order"""
        # Validate that all products exist
        for item in order.items:
            product = await self.product_service.get_product_by_id(item.productId)
            if not product:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Product with ID {item.productId} not found"
                )
        
        order_dict = order.model_dump()
        result = await self.collection.insert_one(order_dict)
        return OrderCreateResponse(id=str(result.inserted_id))

    async def get_orders_by_user(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> OrdersListResponse:
        """Get orders for a specific user with pagination"""
        query = {"userId": user_id}
        
        # Count total documents for pagination
        total_count = await self.collection.count_documents(query)
        
        # Get orders with pagination
        cursor = self.collection.find(query).skip(offset).limit(limit)
        orders = []
        
        async for order in cursor:
            # Get product details for each item in the order
            order_items = []
            for item in order["items"]:
                product = await self.product_service.get_product_by_id(item["productId"])
                if product:
                    product_details = ProductDetails(
                        name=product.name,
                        id=str(product.id)
                    )
                    order_items.append(OrderItemResponse(
                        productDetails=product_details,
                        qty=item["qty"]
                    ))
            
            orders.append(OrderResponse(
                id=str(order["_id"]),
                items=order_items
            ))
        
        # Calculate pagination info
        next_offset = offset + limit if offset + limit < total_count else None
        previous_offset = max(0, offset - limit) if offset > 0 else None
        
        page_info = PageInfo(
            next=next_offset,
            limit=len(orders),
            previous=previous_offset
        )
        
        return OrdersListResponse(data=orders, page=page_info)


# Dependency to get product service
async def get_product_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> ProductService:
    return ProductService(db)


# Dependency to get order service
async def get_order_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> OrderService:
    return OrderService(db)
