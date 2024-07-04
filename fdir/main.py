from auth.database import  DATABASE_URL
from typing import Optional, AsyncGenerator, List
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import  MetaData, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fdir.models import products
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    'http://localhost:3000',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
metadata = MetaData()
Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# Pydantic модель для создания продукта
class ProductCreate(BaseModel):
    product_name: str
    price: int
    description: Optional[str] = None
    in_stock: bool
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    in_stock: Optional[bool] = None
    image_url: Optional[str] = None

class ProductRead(BaseModel):
    id: int
    product_name: str
    price: int
    description: Optional[str] = None
    in_stock: bool
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

async def get_product_by_id(product_id: int, session: AsyncSession) -> Optional[ProductRead]:
    stmt = select(products).where(products.c.id == product_id)
    result = await session.execute(stmt)
    product = result.fetchone()  # Извлечение строки из результата запроса
    if product:
        return ProductRead(
            id=product.id,
            product_name=product.product_name,
            price=product.price,
            description=product.description,
            in_stock=product.in_stock,
            image_url=product.image_url,
        )
    return None

# Маршрут для создания продукта
@app.post("/products/", response_model=ProductCreate)
async def create_product(product: ProductCreate, session: AsyncSession = Depends(get_async_session)):
    query = products.insert().values(
        product_name=product.product_name,
        price=product.price,
        description=product.description,
        in_stock=product.in_stock,
        image_url=product.image_url,
    )
    await session.execute(query)
    await session.commit()
    return product

@app.get("/products/{product_id}/", response_model=ProductRead)
async def read_product(product_id: int, session: AsyncSession = Depends(get_async_session)):
    product = await get_product_by_id(product_id, session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/products/", response_model=List[ProductRead])
async def read_products(session: AsyncSession = Depends(get_async_session)):
    stmt = select(products)
    result = await session.execute(stmt)
    products_list = result.fetchall()
    return [ProductRead(
        id=product.id,
        product_name=product.product_name,
        price=product.price,
        description=product.description,
        in_stock=product.in_stock,
        image_url=product.image_url,
    ) for product in products_list]

@app.delete("/products/{product_id}/", response_model=ProductRead)
async def delete_product(product_id: int, session: AsyncSession = Depends(get_async_session)):
    product = await get_product_by_id(product_id, session)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    delete_stmt = products.delete().where(products.c.id == product_id)
    await session.execute(delete_stmt)
    await session.commit()
    return product

@app.put("/products/{product_id}/", response_model=ProductRead)
async def update_product(product_id: int, product: ProductUpdate, session: AsyncSession = Depends(get_async_session)):
    existing_product = await get_product_by_id(product_id, session)
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    update_data = product.dict(exclude_unset=True)
    query = update(products).where(products.c.id == product_id).values(**update_data)
    await session.execute(query)
    await session.commit()
    return await get_product_by_id(product_id, session)
