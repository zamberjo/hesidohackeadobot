# -*- coding: utf-8 -*-

import db
import os
import sys
import telebot
import logging
import ConfigParser
from utils import show_data
from utils import check_email

_logger = logging.getLogger(__name__)


def check(bot=False, confile=False):
    if not bot and confile:
        Config = ConfigParser.ConfigParser()
        Config.read(confile)
        HSHBOT_TOKEN = Config.get('options', 'api_token')
        bot = telebot.TeleBot(HSHBOT_TOKEN)
        HSHBOT_ADMIN_ID = int(Config.get('options', 'admin_id') or False)
    elif bot:
        HSHBOT_ADMIN_ID = int(os.environ['HSHBOT_ADMIN_ID'])
    else:
        _logger.error("Cron execution error, bot and confile not found!")
        sys.exit()

    _logger.info("cron:: check()")

    if HSHBOT_ADMIN_ID:
        bot.send_message(HSHBOT_ADMIN_ID, '[INFO] Iniciando cron.check()...')

    users = db.get_users()
    emails_checked = {}

    try:
        for user in users:
            user_emails = [] if 'emails' not in user else user['emails']
            if not user_emails:
                bot.send_message(
                    user['id'],
                    "Se ha ejecutado el checkeo de emails, y veo que no tienes ninguno registrado "
                    "aún...\nRecuerda que puedes hacerlo con /newemail"
                )
            flag_update_urls = False
            for user_email in user_emails:
                email_urls = [] if 'urls' not in user_email else user_email['urls']
                email_urls_data = [email_url['url'] for email_url in email_urls]
                flag_notification = False
                if user_email['email'] not in emails_checked:
                    try:
                        json_data = check_email(user_email['email'])
                    except Exception, e:
                        if HSHBOT_ADMIN_ID:
                            bot.send_message(HSHBOT_ADMIN_ID, '[ERROR] HeSidoHackeadoBot is down!')
                        raise e
                    emails_checked[user_email['email']] = show_data(json_data)
                if emails_checked[user_email['email']]:
                    for line in emails_checked[user_email['email']]:
                        registered = False
                        if line[1] in email_urls_data:
                            registered = True
                            break
                        if not registered:
                            line_str = ' '.join(line)
                            if not flag_notification:
                                flag_notification = True
                                bot.send_message(user['id'], "%s con resultados..." % user_email['email'])
                            bot.send_message(user['id'], line_str)
                            email_urls += [{'url': line[1]}]
                            flag_update_urls = True
                    user_email['urls'] = email_urls
                # if not flag_notification:
                #     bot.send_message(user['id'], "%s Todo OK!" % user_email['email'])
            if flag_update_urls:
                db.register_emails(user['id'], user_emails)
    except Exception, e:
        pass
    finally:
        if HSHBOT_ADMIN_ID:
            bot.send_message(HSHBOT_ADMIN_ID, '[INFO] Finalizado cron.check()')
