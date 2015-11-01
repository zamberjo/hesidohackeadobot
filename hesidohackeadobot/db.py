# -*- coding: utf-8 -*-

import os
import logging
import traceback
from pymongo import MongoClient

_logger = logging.getLogger(__name__)
DATABASE = MongoClient().hesidohackeado

def get_user(user_id):
    _logger.info("get_user:: %i" % (user_id))
    try:
        return DATABASE.users.find({"id": user_id})
    except Exception, e:
        traceback.print_exc()
        raise e

def get_users():
    _logger.info("get_users::")
    try:
        return DATABASE.users.find({})
    except Exception, e:
        traceback.print_exc()
        raise e

def register_user(user_id, name, last_name, username):
    _logger.info("register_user:: %i|%s|%s|%r" % (user_id, name, last_name, username))
    try:
        result = DATABASE.users.insert_many([
            {
                "id": user_id,
                "name": name,
                "last_name": last_name,
                "username": username,
                "emails": [],
            }
        ])
    except Exception, e:
        traceback.print_exc()
        raise e

def register_emails(user_id, emails):
    _logger.info("register_email:: %i|%r" % (user_id, emails))
    try:
        DATABASE.users.update_one(
            {"id": user_id},
            {
                "$set": {
                    "emails": emails,
                },
            }
        )
    except Exception, e:
        traceback.print_exc()
        raise e
