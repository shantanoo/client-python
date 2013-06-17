#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instamojo API Client Example

Usage:
    instamojo.py debug
    instamojo.py auth <username> <password>
    instamojo.py auth delete
"""
import os
import json
import logging
import requests

from docopt import docopt



class API():
    endpoint = 'http://local.instamojo.com:5000/api/1/'
    appid = os.getenv('INSTAMOJO_APP_ID', 'test')
    token = None

    def __init__(self, token=None):
        self.token = token

    def save_token_to_file(self, filename='auth.json'):
        try:
            json.dump(self.token, open(filename, 'w+'))
            return True
        except IOError:
            message = 'Unable to open file for saving token: %s' % filename
            logging.error(message)
            raise Exception(message)

    def load_token_from_file(self, filename='auth.json'):
        try:
            self.token = json.load(open(filename, 'r+'))
            return True
        except IOError:
            message = 'Unable to open file for loading token: %s' % filename
            logging.error(message)
            raise Exception(message)

    def api_request(self, method, path, **kwargs):
        headers = {'X-App-Id': self.appid}
        if self.token:
            headers.update({'X-Token-Auth':self.token})

        api_path = self.endpoint + path

        if method == 'GET':
            req = requests.get(api_path, data=kwargs, headers=headers)
        elif method == 'POST':
            req = requests.post(api_path, data=kwargs, headers=headers)
        elif method == 'DELETE':
            req = requests.delete(api_path, data=kwargs, headers=headers)
        else:
            raise Exception('Unable to make a API call for "%s" method.' % method)

        logging.debug('api path: %s' % api_path)
        logging.debug('parameters: %s' % kwargs)
        logging.debug('headers: %s' % headers)
        return json.loads(req.text)

    def debug(self):
        response = self.api_request(method='GET', path='debug/')
        return response

    def auth(self, username, password):
        response = self.api_request(method='POST', path='auth/', username=username, password=password)
        if response['success']:
            self.token = response['token']
        return response

    def delete_auth_token(self):
        if not self.token:
            return Exception('No token loaded, unable to delete.')
        response = self.api_request(method='DELETE', path='auth/%s/' %self.token)
        return response

if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    args = docopt(__doc__, version='Instamojo API Client 1.0')

    logging.info('arguments: %s' % args)

    api = API()

    if args['auth'] and args['delete']:
        api.load_token_from_file()
        print api.delete_auth_token()

    elif args['auth']:
        print api.auth(args['<username>'], args['<password>'])
        api.save_token_to_file()

    elif args['debug']:
        print api.load_token_from_file()
        print api.token
        print api.debug()

