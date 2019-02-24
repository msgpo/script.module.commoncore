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

import sys
from .addon import get_setting, set_property, open_settings, get_name, get_id
from .logger import log
try:
	from urllib.parse import urlparse
	from urllib.parse import urlencode
except ImportError:
	from urllib import urlencode
	from urlparse import urlparse

mode='main'
args = {}
__dispatcher = {}
__args = {}
__kwargs = {}

try:
	args = parse_query(sys.argv[2])
	mode = args['mode']
except:
	args = {"mode": "main"}

try:
	HANDLE_ID = int(sys.argv[1])
	ADDON_URL = sys.argv[0]
	PLUGIN_URL = sys.argv[0] + sys.argv[2]
except:
	HANDLE_ID = -1
	ADDON_URL = 'plugin://%s' % get_name()
	PLUGIN_URL = 'plugin://%s' % get_name()


def _register(mode, target, args=(), kwargs={}):
	if isinstance(mode, list):
		for foo in mode:
			__dispatcher[foo] = target
			__args[foo] = args
			__kwargs[foo] = kwargs
	else:
		__dispatcher[mode] = target
		__args[mode] = args
		__kwargs[mode] = kwargs

def register(mode):
	def func_decorator(func):
		_register(mode, func)
	return func_decorator

def first_run():
	pass

def run():
	if args['mode'] == 'void': return
	if get_setting('setup_run') != 'true' and 'video' in get_id():
		first_run()
	if mode not in ['search_streams', 'play_stream', 'master_control', 'open_settings', 'auth_realdebrid']:
		set_property('last.plugin.url', sys.argv[0] + sys.argv[2])
	if True:#try:
		if args['mode'] == 'addon_settings': 
			open_settings()
			return
		elif args['mode'] is None or not args['mode']:
			__dispatcher[args['main']](*__args[args['main']], **__kwargs[args['main']])
		else:
			__dispatcher[args['mode']](*__args[args['mode']], **__kwargs[args['mode']])
		log("Executing with params: %s | args: %s | kwargs: %s" % (args, __args[args['mode']], __kwargs[args['mode']]))
	#except Exception, e:
	#	log(e)
	#	traceback.print_stack()
	#	handel_error("%s Error" % get_name(), 'Invalid Mode')