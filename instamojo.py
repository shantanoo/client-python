#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Instamojo API Client Example

Usage:
    instamojo.py debug
    instamojo.py auth <username>
    instamojo.py auth --delete
    instamojo.py offer
    instamojo.py offer create [options]
    instamojo.py offer geturl
    instamojo.py offer --slug=<slug>
    instamojo.py offer delete --slug=<slug>

Options:
    --title=<title>
    --description=<description>
    --currency=<currency>
    --base_price=<price>
    --quantity=<quantity>
    --start-date=<start-date>
    --end-date=<end-date>
    --venue=<venue>
    --timezone=<timezone>
    --redirect-url=<redirect-url>
    --note=<note>
    --file-upload-json=<file-upload-json>
    --cover-image-json=<cover-image-json>
    --file=<file>
    --cover=<cover-image>

"""
import os
import json
import logging
import requests
import getpass

from docopt import docopt


class API():
    """
    This is an example client API, kept to bare minimum - including error checking
    to help understand how the API works.
    """
    endpoint = os.getenv('INSTAMOJO_ENDPOINT', 'https://www.instamojo.com/api/1/')
    # Set your APP-ID in environment variables or replace 'test'
    appid = os.getenv('INSTAMOJO_APP_ID', 'test')
    token = None

    def __init__(self, token=None):
        self.token = token

    def save_token_to_file(self, filename='auth.json'):
        """
        Helper function to save Auth-token to a local file for later use.
        """
        try:
            json.dump(self.token, open(filename, 'w+'))
            return True
        except IOError:
            message = 'Unable to open file for saving token: %s' % filename
            logging.error(message)
            raise Exception(message)

    def load_token_from_file(self, filename='auth.json'):
        """
        Helper function to load an Auth-token from a local file.
        """
        try:
            self.token = json.load(open(filename, 'r+'))
            return True
        except IOError:
            message = 'Unable to open file for loading token: %s' % filename
            logging.error(message)
            #raise Exception(message)

    def api_request(self, method, path, **kwargs):
        """
        All API requests are handled here, automatically adds required headers.
        """
        # Header: App-Id
        headers = {'X-App-Id': self.appid}

        # If available, add the Auth-token to header
        if self.token:
            headers.update({'X-Auth-Token':self.token})

        # Build the URL for API call
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
        """
        The one call with minimum fuss.
        """
        response = self.api_request(method='GET', path='debug/')
        return response

    def auth(self, username, password):
        """
        Gets Auth-token
        """
        response = self.api_request(method='POST', path='auth/', username=username, password=password)
        if response['success']:
            self.token = response['token']
        return response

    def delete_auth_token(self):
        """
        Deletes Auth-token from server. This token cannot be used again.
        """
        if not self.token:
            return Exception('No token loaded, unable to delete.')
        response = self.api_request(method='DELETE', path='auth/%s/' %self.token)
        return response

    def offer_list(self):
        """
        Gets a list of offers belonging to user.
        """
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='GET', path='offer')
        return response

    def offer_detail(self, slug):
        """
        Gets details of user's specific offer.
        """
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='GET', path='offer/%s/' % slug)
        return response

    def offer_delete(self, slug):
        """
        Archives offer on server. All web requests to the offer's URLs will result in 404/Not Found.
        """
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='DELETE', path='offer/%s/' % slug)
        return response

    def offer_create(self, **kwargs):
        """
        Creates an offer, expects the required parameters in **kwargs.
        Example:
            offer_create(self, title='Something', description='lorem ipsum'...)
        """
        if not self.token:
            return Exception('No token found!')
        response = self.api_request(method='POST', path='offer/', **kwargs)
        return response

    def get_file_upload_url(self):
        """
        Gets signed upload URL from server, use this to upload file.
        """
        response = self.api_request(method='GET', path='offer/get_file_upload_url/')
        return response

    def upload_file(self, file_upload_url, filepath):
        """
        Helper function to upload file from local path.
        """
        filename = os.path.basename(filepath)
        files = {'fileUpload':(filename, open(filepath, 'rb'))}
        response = requests.post(file_upload_url, files=files)
        return response.text



if __name__ == '__main__':
    # Let's look through the way Instamojo API works,
    # It's a fairly simple RESTful API that lets you
    # work with a user's offers.

    # Setting up logging, you can observe the debug.log file for detailed information.
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)

    # Parsing command-line options. If you haven't seen docopts before,
    # now is a great time to look it up and bookmark it, makes life
    # for commandline app developers so much nicer.
    args = docopt(__doc__, version='Instamojo API Client 1.0')

    # Log raw arguments
    logging.info('arguments: %s' % args)

    # Map the commandline friendly names to actual parameter-names
    options = {'title':'title',
                'description':'description',
                'currency':'currency',
                'base_price':'base_price',
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

    # build the dictionary for data
    for option in options:
        if args.has_key('--%s' % option):
            formdata.update({options[option]: args['--%s' % option]})

    # Create an instance of the example API
    api = API()
    if api.load_token_from_file():
        logging.info('API token loaded from file.')
    else:
        logging.info('Unable to load API token from file.')

    # here onwards, we look at what arguments are passed to us,
    # and call the appropriate API methods.
    if args['auth'] and args['--delete']:
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
                logging.info('Got file upload URL: %s' % file_upload_url)
            else:
                raise Exception('Unable to get file upload url from API. Got this instead: %s' % file_upload_url)

            file_upload_json = api.upload_file(file_upload_url, args['--file'])
            print file_upload_json

            # inject the json data into formdata
            formdata['file_upload_json'] = file_upload_json

        if args['--cover']:
            # we first need to upload the file, get the json
            # and put it in formdata.file_upload_json
            cover_upload_url = api.get_file_upload_url()
            if cover_upload_url.get('success',False):
                cover_upload_url = cover_upload_url['upload_url']
                logging.info('Got cover image upload URL: %s' % cover_upload_url)
            else:
                raise Exception('Unable to get cover image upload url from API. Got this instead: %s' % cover_upload_url)

            cover_image_json = api.upload_file(cover_upload_url, args['--cover'])
            print cover_image_json

            # inject the json data into formdata
            formdata['cover_image_json'] = cover_image_json


        # finally, create the offer
        print formdata
        print api.offer_create(**formdata)

    elif args['offer'] and args['geturl']:
        print api.get_file_upload_url()

    elif args['offer'] and args['delete'] and args['--slug']:
        print api.offer_delete(args['--slug'])

    elif args['offer'] and args['--slug']:
        print api.offer_detail(args['--slug'])

    elif args['offer']:
        print api.offer_list()
