#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instamojo API Client Example

Usage:
    instamojo.py debug
    instamojo.py auth <username>
    instamojo.py auth delete
    instamojo.py offer
    instamojo.py offer create [options]
    instamojo.py offer geturl
    instamojo.py offer --slug=<slug>
    instamojo.py offer delete --slug=<slug>

Options:
    --title=<title>
    --description=<description>
    --inr=<inr>
    --usd=<usd>
    --quantity=<quantity>
    --start-date=<start-date>
    --end-date<end-date>
    --venue=<venue>
    --timezone=<timezone>
    --redirect-url=<redirect-url>
    --note=<note>
    --file-upload-json=<file-upload-json>
    --cover-image-json=<cover-image-json>
    --file==<file>
"""
import os
import json
import logging
import requests
import getpass

from docopt import docopt


class API():
    endpoint = 'https://staging.instamojo.com/api/1/'
    #endpoint = 'http://local.instamojo.com:5000/api/1/'
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
            #raise Exception(message)

    def api_request(self, method, path, **kwargs):
        headers = {'X-App-Id': self.appid}
        if self.token:
            headers.update({'X-Auth-Token':self.token})

        api_path = self.endpoint + path

        if method == 'GET':
            req = requests.get(api_path, data=kwargs, headers=headers)
        elif method == 'POST':
            req = requests.post(api_path, data=kwargs, headers=headers)
        elif method == 'DELETE':
            req = requests.delete(api_path, data=kwargs, headers=headers)
        elif method == 'PUT':
            req = requests.put(api_path, data=kwargs, headers=headers)
        else:
            raise Exception('Unable to make a API call for "%s" method.' % method)

        logging.debug('api path: %s' % api_path)
        logging.debug('parameters: %s' % kwargs)
        logging.debug('headers: %s' % headers)
        try:
            return json.loads(req.text)
        except:
            raise Exception('Unable to decode response. Expected JSON, got this: \n\n\n %s' % req.text)

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

    def offer_list(self):
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='GET', path='offer')
        return response

    def offer_detail(self, slug):
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='GET', path='offer/%s/' % slug)
        return response

    def offer_delete(self, slug):
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='DELETE', path='offer/%s/' % slug)
        return response

    def offer_create(self, **kwargs):
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='POST', path='offer/', **kwargs)
        return response

    def get_file_upload_url(self):
        response = self.api_request(method='GET', path='offer/get_file_upload_url/')
        return response

    def upload_file(self, file_upload_url, filepath):
        filename = os.path.basename(filepath)
        files = {'fileUpload':(filename, open(filepath, 'rb'))}
        response = requests.post(file_upload_url, files=files)
        return response.text



if __name__ == '__main__':
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    args = docopt(__doc__, version='Instamojo API Client 1.0')

    logging.info('arguments: %s' % args)

    options = {'title':'title',
                'description':'description',
                'inr':'base_inr',
                'usd':'base_usd',
                'quantity':'quantity',
                'start-date':'start_date',
                'end-date':'end_date',
                'venue':'venue',
                'timezone':'timezone',
                'redirect-url':'redirect_url',
                'note':'note',
                'file-upload-json':'file_upload_json',
                'cover-image-json':'cover_image_json',
                }
    formdata = {}
    for option in options:
        if args.has_key('--%s' % option):
            formdata.update({options[option]: args['--%s' % option]})

    api = API()
    if api.load_token_from_file():
        print 'API token loaded from file.'

    if args['auth'] and args['delete']:
        print api.delete_auth_token()

    elif args['auth']:
        password = getpass.getpass()
        print api.auth(args['<username>'], password)
        api.save_token_to_file()

    elif args['debug']:
        print api.debug()

    elif args['offer'] and args['create']:
        if args['--file']:
            # we first need to upload the file, get the json
            # and put it in formdata.file_upload_json
            file_upload_url = api.get_file_upload_url()
            if file_upload_url.get('success',False):
                file_upload_url = file_upload_url['upload_url']
            else:
                raise Exception('Unable to get file upload url from API. Got this instead: %s' % file_upload_url)

            print args['--file']
            file_upload_json = api.upload_file(file_upload_url, args['--file'])

            print file_upload_json

            formdata['file_upload_json'] = file_upload_json
        print api.offer_create(**formdata)

    elif args['offer'] and args['geturl']:
        print api.get_file_upload_url()

    elif args['offer'] and args['delete'] and args['--slug']:
        print api.offer_delete(args['--slug'])

    elif args['offer'] and args['--slug']:
        print api.offer_detail(args['--slug'])

    elif args['offer']:
        print api.offer_list()

