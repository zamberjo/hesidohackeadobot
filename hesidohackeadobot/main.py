# -*- coding: utf-8 -*-

import os
import db
import re
import cron
import json
import time
import logging
import telebot
import datetime
import requests
import threading
from utils import show_data
from utils import check_email
from telebot import types

_logger = logging.getLogger(__name__)
bot = telebot.TeleBot(os.environ["HSHBOT_TOKEN"])

TEXT_MESSAGES = {
    'help':
        u"/newemail - Registra un nuevo email.\n"
        u"/delemail - Borra un email registrado.\n"
        u"/delemails - Borra todos los emails registrados.\n"
        u"/emails - Devuelve todos los emails registrados hasta el momento.\n"
        u"/checkunread - Ejecuta la consulta a la api de hesidohackeado. Sólo muestra los resultados no leidos.\n"
        u"/checkall - Ejecuta la consulta a la api de hesidohackeado. Muestra todos los resultados obtenidos.\n"
        u"/notices - Muestra las últimas noticias del bot.\n"
        u"/help - Muestra esta ayuda.\n",

    'info':
        u"La verificación se ejecuta cada 6 horas.\nEn caso de no obtener NUEVOS "
        u"resultados de la api, no notifica nada, en caso contrario HeSidoHackeadoAPI nos enviará "
        u"el link de descarga del fichero",
}

def process_register_email(message):
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", message.text):
            bot.reply_to(message, 'Email incorrecto. Vuelve a introducirlo.')
            bot.register_next_step_handler(msg, process_register_email)
        else:
            user = db.get_user(message.from_user.id)[0]
            emails = [] if 'emails' not in user else user['emails']
            registered = False
            for email in emails:
                if email['email'] == message.text:
                    registered = True
                    break
            if not registered:
                emails += [{
                        'email': message.text,
                        'urls': [{
                            'url': '',
                        }],
                }]
                db.register_emails(user['id'], emails)
                bot.reply_to(message, 'Registrado!')
            else:
                bot.reply_to(message, 'Este email ya lo has registrado. Se ignora.')
    except Exception, e:
        bot.reply_to(message, 'ERROR')

@bot.message_handler(commands=['newemail'])
def handle_newemail(message):
    _logger.info("/newemail")
    if message.text != '/newemail':
        process_register_email(message)
    else:
        msg = bot.reply_to(message, 'Dime que email registrar')
        bot.register_next_step_handler(msg, process_register_email)
    return False

def process_delete_email(message):
    markup = types.ReplyKeyboardHide(selective=False)
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", message.text):
            bot.reply_to(message, 'Email incorrecto.')
            bot.register_next_step_handler(msg, process_delete_email)
        else:
            user = db.get_user(message.from_user.id)[0]
            emails = [] if 'emails' not in user else user['emails']
            registered = False
            new_emails = []
            for email in emails:
                if email['email'] == message.text:
                    registered = True
                else:
                    new_emails += [email]
            if registered:
                db.register_emails(user['id'], new_emails)
            else:
                bot.reply_to(message, 'Este email no está registrado. Se ignora.')
            bot.reply_to(message, 'Se ha borrado dicho dicho email.', reply_markup=markup)
    except Exception, e:
        HSHBOT_ADMIN_ID = int(os.environ['HSHBOT_ADMIN_ID'])
        if HSHBOT_ADMIN_ID:
            bot.send_message(HSHBOT_ADMIN_ID, 'ERROR', reply_markup=markup)

@bot.message_handler(commands=['delemail'])
def handle_delemail(message):
    _logger.info("/delemail")
    if message.text != '/delemail':
        process_delete_email(message)
    else:
        markup = types.ReplyKeyboardMarkup()
        user = db.get_user(message.from_user.id)[0]
        emails = [] if 'emails' not in user else user['emails']
        if emails:
            for email in emails:
                markup.row(email['email'])
            msg = bot.reply_to(message, 'Dime que email borrar', reply_markup=markup)
            bot.register_next_step_handler(msg, process_delete_email)
        else:
            bot.reply_to(message, "No has registrado emails todavía. Utiliza /newemail para ello.")
    return False

@bot.message_handler(commands=['emails'])
def handle_emails(message):
    _logger.info("/emails")
    user = db.get_user(message.from_user.id)[0]
    emails = [] if 'emails' not in user else user['emails']
    emails_str = ''
    for email in emails:
        emails_str += email['email'] + "\n"
    if emails_str:
        bot.reply_to(message, emails_str)
    else:
        bot.reply_to(
            message,
            "No has registrado emails todavía. Utiliza /newemail para ello."
        )
    return False

@bot.message_handler(commands=["ping"])
def on_ping(message):
    bot.reply_to(message, "pong")

@bot.message_handler(commands=['delemails'])
def handle_delemails(message):
    _logger.info("/delemails")
    user = db.get_user(message.from_user.id)[0]
    if user['emails'] != []:
        db.register_emails(user['id'], [])
        bot.reply_to(message, 'Se han borrado todos los emails registrados.')
    else:
        bot.reply_to(message, 'No has registrado emails todavía. Utiliza /newemail para ello.')
    return False

@bot.message_handler(commands=['start'])
def handle_start(message):
    _logger.info("/start")
    bot.reply_to(message, "Welcome!")
    users = db.get_user(message.from_user.id)
    if users.count() == 0:
        db.register_user(
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username)

@bot.message_handler(commands=['users'])
def handle_users(message):
    _logger.info("/users")
    HSHBOT_ADMIN_ID = int(os.environ['HSHBOT_ADMIN_ID'])
    if message.from_user.id == HSHBOT_ADMIN_ID:
        users = db.get_users()
        users_str = ''
        for user_data in users:
            users_str += '%i - ' % (user_data['id'])
            if user_data['username']:
                users_str += '(%s) ' % (user_data['username'])
            users_str += '%s %s emails=%i\n' % (
                user_data['name'], user_data['last_name'], len(user_data['emails']))
        bot.reply_to(message, users_str)

@bot.message_handler(commands=['croncheck'])
def handle_users(message):
    _logger.info("/croncheck")
    HSHBOT_ADMIN_ID = int(os.environ['HSHBOT_ADMIN_ID'])
    if message.from_user.id == HSHBOT_ADMIN_ID:
        cron.check(bot)

@bot.message_handler(commands=['checkunread'])
def handle_checkunread(message):
    _logger.info("/checkunread")
    user = db.get_user(message.from_user.id)[0]
    emails = [] if 'emails' not in user else user['emails']
    if not emails:
        bot.reply_to(message, 'No has registrado emails todavía. Utiliza /newemail para ello.')
    else:
        flag_update_urls = False
        for email in emails:
            urls = [] if 'urls' not in email else email['urls']
            urls_data = [url['url'] for url in urls]
            json_data = check_email(email['email'])
            lines = show_data(json_data)
            flag_notification = False
            if lines:
                for line in lines:
                    registered = False
                    if line[1] in urls_data:
                        registered = True
                        break
                    if not registered:
                        line_str = ' '.join(line)
                        if not flag_notification:
                            flag_notification = True
                            bot.send_message(user['id'], "%s con resultados..." % email['email'])
                        bot.send_message(user['id'], line_str)
                        urls += [{'url': line[1]}]
                        flag_update_urls = True
                email['urls'] = urls
            if not flag_notification:
                bot.send_message(user['id'], "%s Todo OK!" % email['email'])
        if flag_update_urls:
            db.register_emails(user['id'], emails)

@bot.message_handler(commands=['checkall'])
def handle_checkall(message):
    _logger.info("/checkall")
    user = db.get_user(message.from_user.id)[0]
    emails = [] if 'emails' not in user else user['emails']
    if not emails:
        bot.reply_to(message, 'No has registrado emails todavía. Utiliza /newemail para ello.')
    flag_update_urls = False
    for email in emails:
        urls = [] if 'urls' not in email else email['urls']
        urls_data = [url['url'] for url in urls]
        json_data = check_email(email['email'])
        lines = show_data(json_data)
        if lines:
            bot.reply_to(message, "%s con resultados..." % email['email'])
            for line in lines:
                registered = False
                if line[1] in urls_data:
                    registered = True
                    break
                if not registered:
                    urls += [{'url': line[1]}]
                    flag_update_urls =True
                line_str = ' '.join(line)
                bot.send_message(user['id'], line_str)
            email['urls'] = urls
        else:
            bot.send_message(user['id'], "%s Todo OK!" % email['email'])
    if flag_update_urls:
        db.register_emails(user['id'], emails)

@bot.message_handler(commands=['help'])
def handle_help(message):
    _logger.info("/help")
    bot.reply_to(message, TEXT_MESSAGES['help'])

@bot.message_handler(commands=['info'])
def handle_notices(message):
    _logger.info("/info")
    bot.reply_to(message, TEXT_MESSAGES['info'])

def start():
    _logger.info("main:: start()")
    bot.polling(none_stop=True)

