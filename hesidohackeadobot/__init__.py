# -*- coding: utf-8 -*-

__author__ = 'Jose Zambudio Bernabeu'

import os
import sys
import cron
import logging
import argparse
import traceback
import ConfigParser
from crontab import CronTab

def do_cron_record(cron_minute_on, cron_minute_every, cron_hour_on, cron_hour_every, confile):
    # crontab for user hshbot
    my_user_cron = CronTab(user=True)

    # Reset last job
    my_user_cron.remove_all(comment='HeSidoHAckeadoBotCron')

    # Create new job
    job  = my_user_cron.new(
        command='python -c "import hesidohackeadobot; hesidohackeadobot.cron.check(bot=False, confile=\'%s\')"' % (confile),
        comment='HeSidoHAckeadoBotCron'
    )

    # Minutes
    if cron_minute_on:
        job.minute.on(cron_minute_on)
    if cron_minute_every:
        job.minute.every(cron_minute_every)

    # Seconds
    if cron_hour_on:
        job.hour.on(cron_hour_on)
    if cron_hour_every:
        job.hour.every(cron_hour_every)

    # Write on crontab
    my_user_cron.write()

def start():
    try:
        parser = argparse.ArgumentParser(
            prog="hshbot.py",
            description="HeSidoHackeadoBot command line"
        )

        parser.add_argument(
            '--confile', metavar='confile', type=unicode, nargs=1, help='Specifies the configuration file',
            default='/etc/hshbot/hesidohackeado-bot.conf', required=True)

        parser.add_argument(
            '--logfile', metavar='logfile', type=unicode, nargs=1, help='Specifies the log file',
            default='/var/log/hshbot/hesidohackeado-bot.log')
        args = parser.parse_args()

        FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        if args.logfile:
            logging.basicConfig(
                format=FORMAT,
                filename=args.logfile[0],
                level=logging.INFO
            )
            _logger = logging.getLogger(__name__)
        else:
            logging.basicConfig(
                format=FORMAT,
                stream=sys.stdout,
                level=logging.DEBUG
            )
            _logger = logging.getLogger(__name__)

        Config = ConfigParser.ConfigParser()
        Config.read(args.confile[0])

        # Admin id for telegram
        os.environ['HSHBOT_ADMIN_ID'] = str(Config.get('options', 'admin_id') or False)

        # Cron scheduler
        try:
            cron_hour_every = int(Config.getint('options', 'cron_hour_every'))
        except Exception, e:
            cron_hour_every = 6

        try:
            cron_hour_on = int(Config.getint('options', 'cron_hour_on'))
        except Exception, e:
            cron_hour_on = False

        try:
            cron_minute_every = int(Config.getint('options', 'cron_minute_every'))
        except Exception, e:
            cron_minute_every = False

        try:
            cron_minute_on = int(Config.getint('options', 'cron_minute_on'))
        except Exception, e:
            cron_minute_on = False

        # Telegram API conf
        try:
            os.environ["HSHBOT_TOKEN"] = Config.get('options', 'api_token')
            if Config.get('options', 'api_token') == "False":
                sys.exit()
        except Exception, e:
            _logger.error("api_token must be specified on config file!")
            sys.exit()

        # Cron Record.
        _logger.info('cron_minute_on = %r' % (cron_minute_on))
        _logger.info('cron_minute_every = %r' % (cron_minute_every))
        _logger.info('cron_hour_on = %r' % (cron_hour_on))
        _logger.info('cron_hour_every = %r' % (cron_hour_every))
        do_cron_record(cron_minute_on, cron_minute_every, cron_hour_on, cron_hour_every, args.confile[0])

        # Start!
        import main
        import db
        main.start()
    except Exception, e:
        traceback.print_exc()
        raise e
