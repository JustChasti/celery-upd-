import json
from loguru import logger
from flask import Flask, request, jsonify
from src import db
from modules import parser


application = Flask(__name__)


@application.route("/")
def hello():
   return "<h1 style='color:blue'>Hello There!</h1>"


@application.route("/links/all/", methods=["GET"])
def get_all():
    """Add a new link to base"""
    return jsonify(db.get_all())


@application.route("/links/parse/", methods=["GET"])
def send_urls():
    """Send links to parser"""
    return jsonify(db.get_links())


@application.route("/links/update/", methods=["PUT"])
def get_parse_urls():
    """Get links from parser and update in base"""
    j_request = request.get_json(force=True)
    db.update_link(j_request[0]['url'], j_request[0]['Name'],
                   j_request[0]['Price'], j_request[0]['Art'],
                   j_request[0]['Col_otz'], j_request[0]['rating'],
                   j_request[0]['description'], j_request[0]['properties'],
                   j_request[1])
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@application.route("/links/add/", methods=["POST"])
def get_link():
    """Add a new link to base"""
    j_request = request.json
    try:
        db.append_link(j_request['link'])
    except Exception as e:
        logger.exception(e)
    try:
        product, reviews = parser.parse_wb(j_request['link'])
        db.update_link(product['url'], product['Name'],
                       product['Price'], product['Art'],
                       product['Col_otz'], product['rating'],
                       product['description'],
                       product['properties'],
                       reviews)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    application.run()
