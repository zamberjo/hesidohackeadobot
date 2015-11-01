# -*- coding: utf-8 -*-

import requests
import json
import logging
_logger = logging.getLogger(__name__)


def show_data(json_data):
    lines = []
    try:
        if json_data['status'] == 'found':
            header = [u'date_leaked', u'source_url']
            for line in json_data['data']:
                lines += [[
                    str(line['date_leaked']),
                    str(line['source_url']),
                ]]
    except Exception, e:
        _logger.error(e)
        raise e
    return lines

def check_email(email):
    try:
        url = 'https://hesidohackeado.com/api'
        params = {
            'q': '%s' % (email),
        }
        response = requests.get(url=url, params=params).text
    except Exception, e:
        _logger.error(e)
        raise e
    return json.loads(response)
