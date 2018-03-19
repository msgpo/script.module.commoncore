# -*- coding: utf-8 -*-

'''*
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*'''

import urllib
import traceback
import requests
from dillinger.common import kodi
from dillinger.common.baseapi import DB_CACHABLE_API as BASE_API, EXPIRE_TIMES

CLIENT_ID = 'MUQMIQX6YWDSU'
class RealDebrid_API(BASE_API):
	base_url = 'https://api.real-debrid.com/rest/1.0'
	default_return_type = 'json'
	headers = {}
	attemp = 0
	timeout = 10
	def authorize(self):
		self.headers = {"Authorization": "Bearer %s" % kodi.get_setting('realdebrid_token', addon_id='script.module.scrapecore')}

	def handel_error(self, error, response, request_args, request_kwargs):
		if response is None: raise error
		if response.status_code == 401 and request_kwargs['auth'] and self.attemp == 0:
			self.attempt = 1
			refresh_token()
			return self.request(*request_args, **request_kwargs)
			
	
RD = RealDebrid_API()
session = requests.Session()

def authorize():
	PB = kodi.ProgressBar()
	PB.new("Authorize RealDebrid: https://real-debrid.com/device", 600)
	response = request_code()
	device_code = response['device_code']
	user_code = response['user_code']
	timeout = response['expires_in']
	PB.update_subheading("Enter Code: %s" % user_code, "%s sec(s)" % 600)
	
	for tick in range(600, 0,-1):
		if PB.is_canceled(): return
		percent =  int((tick / 600.0) * 100)
		PB.update_subheading("Enter Code: %s" % user_code, "%s sec(s) remaining" % tick, percent=percent)
		if (tick % 5) == 0:
			r = poll_credentials(device_code)
			if r:
				client_id = r['client_id']
				client_secret = r['client_secret']
				token = request_token(client_id, client_secret, device_code)
				kodi.set_setting('realdebrid_client_id', client_id, addon_id='script.module.scrapecore')
				kodi.set_setting('realdebrid_client_secret', client_secret, addon_id='script.module.scrapecore')
				kodi.set_setting('realdebrid_token', token['access_token'], addon_id='script.module.scrapecore')
				kodi.set_setting('realdebrid_refresh_token', token['refresh_token'], addon_id='script.module.scrapecore')
				PB.close()
				kodi.notify("RealDebrid Authorization", "Success!")
				return

		kodi.sleep(1000)

def poll_credentials(device_code):
	try:	
		r = request_credentials(device_code)
		client_id = r['client_id']
	except: return False	
	return r

def request_code():
	url = 'https://api.real-debrid.com/oauth/v2/device/code'
	query = {"client_id": CLIENT_ID, "new_credentials": "yes"}
	response = session.get(url, params=query)
	return response.json()

def request_credentials(device_code):
	url = 'https://api.real-debrid.com/oauth/v2/device/credentials'
	query = {"client_id": CLIENT_ID, "code": device_code}
	response = session.get(url, params=query)
	return response.json()

def request_token(client_id, client_secret, code):
	url = 'https://api.real-debrid.com/oauth/v2/token'
	data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
	response = session.post(url, data=data)
	return response.json()

def refresh_token():
	url = 'https://api.real-debrid.com/oauth/v2/token'
	data = {'client_id': kodi.get_setting('realdebrid_client_id', addon_id='script.module.scrapecore'), 'client_secret': kodi.get_setting('realdebrid_client_secret', addon_id='script.module.scrapecore'), 'code': kodi.get_setting('realdebrid_refresh_token', addon_id='script.module.scrapecore'), 'grant_type': 'http://oauth.net/grant_type/device/1.0'}
	response = session.post(url, data=data)
	response.json()
	if 'access_token' in response:
		kodi.set_setting('realdebrid_token', response['access_token'], addon_id='script.module.scrapecore')
	return response		

def get_hosts(full=False):
	uri = '/hosts'
	results = RD.request(uri, cache_limit=EXPIRE_TIMES.EIGHTHOURS)
	if full: return results
	else: return [h for h in results][1:-1]

def verify_link(link):
	uri = '/unrestrict/check'
	post_data= {'link': link}
	response = RD.request(uri, data=post_data, cache_limit=EXPIRE_TIMES.EIGHTHOURS)
	return response

def resolve_url(link):
	resolved_url = ''
	uri = '/unrestrict/link'
	post_data= {'link': link}
	response = RD.request(uri, data=post_data, auth=True)

	if response and 'download' in response:
		return response['download']
	else: 
		return ''


