#!/usr/bin/python
#
# Copyright (c) 2012, Benjamin Staffin
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the organization nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""A simple urlopen wrapper that handles basic http authentication."""

import getpass
import logging
import urllib2
import sys


def GetUrl(url, username=None, password=None):
  """Fetch a http url, with username and password if supplied.

  Does not handle any exceptions.

  Args:
    username: username to use.
    password: password to use.
  Returns:
    Direct return value of urllib2.urlopen()
  """
  if username:
    # Create a password manager.
    passman = urllib2.HTTPPasswordMgrWithDefaultRealm()

    # Use None as the realm name so urllib2 will always use these credentials.
    passman.add_password(None, url, username, password)

    # Create the auth handler.
    authhandler = urllib2.HTTPBasicAuthHandler(passman)
    
    # Use our auth handler to make an opener object.
    opener = urllib2.build_opener(authhandler)

    # Install our opener as the default opener in urllib2, so all calls to
    # urlopen will use it.
    urllib2.install_opener(opener)

  return urllib2.urlopen(url)


def FancyGetUrl(url, username=None, password=None, auth=True, prompt=True):
  """Fetch a http url, optionally with http basic authentication.

  If auth=True and username and/or password or blank, interactively prompt the
  user for them

  Args:
    username: username to use.
    password: password to use.
    auth: Boolean. If true, retry with basic auth if required.
    prompt: Boolean. If true, prompt the user for username and password if
            required.
  Returns:
    Direct output(s) of urllib2.urlopen(), which is a file-like object.
  Raises:
    urllib2.HTTPError: Failed to get the url.
  """
  try:
    response = GetUrl(url)
  except urllib2.HTTPError as e:
    if hasattr(e, 'code'):
      if e.code == 401:
        if not auth:
          logging.error('Auth required but disabled.')
          raise
        logging.info('Retrying with http auth.')
        try:
          if prompt:
            if not username:
              username = raw_input('Username: ')
            if not password:
              password = getpass.getpass()
          response = GetUrl(url, username, password)
        except urllib2.HTTPError as e:
          raise
      else:
        logging.error('Failed to get %s:' % url)
        logging.error('%s: %s' % (e.code, e.msg))
        return
  return response


def __main(args):
  while len(args) < 3:
    args.append(None)
  url = args[0] or raw_input('URL: ')
  username = args[1]
  password = args[2]
  try:
    response = FancyGetUrl(url, username, password)
  except urllib2.HTTPError as e:
    logging.error('Failed to get %s:' % url)
    logging.error('%s: %s' % (e.code, e.msg))
    logging.error('Gave up.')
    return 1
  print response.read()


if __name__ == '__main__':
  sys.exit(__main(sys.argv[1:]))
