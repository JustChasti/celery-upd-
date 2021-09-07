from time import sleep
import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, sql, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from loguru import logger

from config import base_user, base_pass, base_name, base_host, base_port

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password = Column(String(200))
    firstname = Column(String(100))
    lastname = Column(String(100))
    activate_token = Column(String(200))
    email_verified_at = Column(DateTime())
    status = Column(Integer)
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    products = relationship("Product", back_populates="user")
    tokens = relationship("Token", back_populates="user")
    forgot_passwords = relationship("ForgotPassword", back_populates="user")


class ForgotPassword(Base):
    __tablename__ = "forgot_passwords"

    id = Column(Integer, primary_key=True)
    token = Column(String(200), unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    created_at = Column(DateTime())

    user = relationship(User, back_populates="forgot_passwords")

    def __init__(self, token: str, user_id: int):
        self.token, self.user_id = token, user_id
        self.created_at = datetime.now()

        super(ForgotPassword, self).__init__()


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True)
    access_token = Column(String(200))
    refresh_token = Column(String(200), unique=True)
    user_id = Column(Integer, ForeignKey(User.id))
    created_at = Column(DateTime())

    user = relationship(User, back_populates="tokens")

    def __init__(self, access_token: str, refresh_token: str, user_id: int):
        self.access_token = access_token,
        self.refresh_token = refresh_token
        self.user_id = user_id
        self.created_at = datetime.datetime.now()

        super(Token, self).__init__()


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    url = Column(String(100), unique=True)
    is_active = Column("is_active", Boolean(), server_default=sql.expression.true())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    products = relationship("Product", back_populates="shop")

    def __init__(self, name: str, url: str):
        self.name, self.url = name, url
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

        super(Shop, self).__init__()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    url = Column(String(100), unique=True)
    article = Column(String(100), unique=True, nullable=True)
    description = Column(Text, nullable=True)
    properties = Column(JSON, nullable=True)
    shop_id = Column(Integer, ForeignKey(Shop.id), nullable=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=True)
    is_active = Column("is_active", Boolean(), server_default=sql.expression.true())
    created_at = Column(DateTime())
    updated_at = Column(DateTime())

    statistics = relationship("Statistics", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    shop = relationship(Shop, back_populates="products")
    user = relationship(User, back_populates="products")


class Review(Base):
    __tablename__ = 'rewiews'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    user = Column(String(64), nullable=False)
    mark = Column(Integer, nullable=False)
    comment = Column(String(10000), nullable=False)
    product = relationship(Product, back_populates="reviews")

    def __init__(self, user: str, mark: int, comment: str):
        self.user, self.mark, self.comment = user, mark, comment
        self.created_at = datetime.now()

        super(Review, self).__init__()


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)
    col_otz = Column(Integer, nullable=True)
    product_id = Column(Integer, ForeignKey(Product.id))
    created_at = Column(DateTime())

    product = relationship(Product, back_populates="statistics")


data = {
    'drivername': 'postgresql+psycopg2',
    'host': base_host,
    'port': base_port,
    'username': base_user,
    'password': base_pass,
    'database': base_name,
}
"""
data = {
    'drivername': 'postgresql+psycopg2',
    'host': 'localhost',
    'port': '5432',
    'username': 'postgres',
    'password': 'qm7hFSIW',
    'database': 'parse_markets',
}
"""

while True:
    try:
        engine = create_engine(URL(**data))
        engine.connect()
        Base.metadata.create_all(engine)
        break
    except Exception as e:
        logger.warning('I cant connect to database. Creating her***')
        try:
            connection = psycopg2.connect(user=base_user, password=base_pass)
            connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = connection.cursor()
            sql_create_database = cursor.execute("create database " + 'parse_markets')
            cursor.close()
            connection.close()
            engine = create_engine(URL(**data))
            engine.connect()
            Base.metadata.create_all(engine)
            Base.metadata.bind = engine
            break
        except Exception as e:
            logger.exception("Postgres connection error")
            sleep(5)

Session = sessionmaker(bind=engine)
