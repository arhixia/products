from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, MetaData, Table, Boolean

metadata = MetaData()

products = Table(
    'products',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('product_name', String, nullable=False),
    Column('price', Integer, nullable=False),
    Column('description', String, nullable=True),
    Column('in_stock', Boolean, nullable=False),
    Column('image_url', String)  # Новая колонка для хранения URL изображения товара
)

user = Table(
    'user',
    metadata,
    Column('id',Integer,primary_key=True),
    Column('username',String,nullable=False),
    Column('hashed_password',String,nullable=False),
    Column('email',String,nullable=False),
    Column('is_active',Boolean,default=True,nullable=False),
    Column('is_verified', Boolean,default=False, nullable=False),
    Column('is_superuser', Boolean,default=False, nullable=False),
    )
