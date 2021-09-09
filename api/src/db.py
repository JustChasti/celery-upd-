import sys
import os
from loguru import logger
import psycopg2
import config
import datetime

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

from src.base import Product, Review, Statistics
from src.base import Session


def append_link(link):
    session = Session()
    try:
        link = Product(url=link, is_active=True,
                       created_at=datetime.datetime.now(),
                       updated_at=datetime.datetime.now())
        session.add(link)
        session.commit()
    except Exception as e:
        link = Product(url=link, is_active=True,
                       created_at=datetime.datetime.now(),
                       updated_at=datetime.datetime.now())
        session.add(link)
        session.commit()
    session.close()


def update_link(link, name, price, articul, k_otz, rating, description, properties, rev_list):
    session = Session()
    try:
        product = session.query(Product).filter(Product.url == link).one()
        if product.name != name or product.article != articul or product.description != description or product.properties != properties:
            product.name = name
            product.article = articul
            product.description = description
            product.properties = properties
            session.add(product)
        try:
            stats = session.query(Statistics).filter(Statistics.product_id == product.id).one()
            if stats.price != int(price) or stats.col_otz != int(k_otz) or stats.rating != int(rating):
                stats = Statistics(price=int(price), rating=int(rating),
                                   col_otz=int(k_otz), product_id=product.id,
                                   created_at=datetime.datetime.now())
                session.add(stats)
        except Exception as e:
            stats = Statistics(price=int(price), rating=int(rating),
                               col_otz=int(k_otz), product_id=product.id,
                               created_at=datetime.datetime.now())
            session.add(stats)

        id = product.id
        session.commit()
        session.close()
        update_reviews(id, rev_list)
    except Exception as e:
        logger.exception(e)


def update_reviews(link_id, rev_list):
    session = Session()
    for i in rev_list:
        try:
            review = session.query(Review).filter(Review.product_id == link_id,
                                                  Review.comment == i['Com']).one()
        except Exception as e:
            review = Review(product_id=link_id, user=i['Name'],
                            mark=int(i['Mark']), comment=i['Com'])
            session.add(review)
    session.commit()
    session.close()


def get_links():
    session = Session()
    try:
        links = session.query(Product).all()
        print(links)
        urls = []
        for i in links:
            req = {}
            req['url'] = i.url
            urls.append(req)
        return urls
    except Exception as e:
        return []
    session.close()


def get_all():
    session = Session()
    try:
        links = session.query(Product).all()
        for i in links:
            print(vars(i))
        links = session.query(Review).all()
        for i in links:
            print(vars(i))
        links = session.query(Statistics).all()
        for i in links:
            print(vars(i))
    except Exception as e:
        logger.exception(e)
    session.close()


if __name__ == "__main__":
    pass
