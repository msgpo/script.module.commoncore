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
import json
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
from .constants import *

try:
	from urllib.parse import urlparse
	from urllib.parse import urlencode
except ImportError:
	from urllib import urlencode
	from urlparse import urlparse

__addon = xbmcaddon.Addon()
__get_setting = __addon.getSetting
__set_setting = __addon.setSetting
show_settings = __addon.openSettings
sleep = xbmc.sleep
get_condition_visiblity = xbmc.getCondVisibility

#try:
#	HANDLE_ID = int(sys.argv[1])
#except:
#	HANDLE_ID = -1

def get_kodi_version():
	full_version_info = xbmc.getInfoLabel('System.BuildVersion')
	return int(full_version_info.split(".")[0])

def get_addon(addon_id):
	return xbmcaddon.Addon(addon_id)

def has_addon(addon_id):
	return get_condition_visiblity("System.HasAddon(%s)" % addon_id)==1

def get_window(id=10000):
	return xbmcgui.Window(id)

def get_path():
	return __addon.getAddonInfo('path')

def get_profile():
	return __addon.getAddonInfo('profile')

def translate_path(path):
	return xbmc.translatePath(path)

def get_version():
	return __addon.getAddonInfo('version')

def get_id():
	return __addon.getAddonInfo('id')

def get_name():
	return __addon.getAddonInfo('name')

def open_settings(addon_id=None):
	if not addon_id or addon_id is None:
		show_settings()
	else:
		get_addon(addon_id).openSettings()

def get_property(k, id=None):
	if id is None: id = get_id()
	p = get_window().getProperty('%s.%s' % (id, k))
	if p.lower() == 'false': return False
	if p.lower() == 'true': return True
	return p
	
def set_property(k, v, id=None):
	if id is None: id = get_id()
	get_window().setProperty('%s.%s' % (id, k), str(v))

def clear_property(k, id=None):
	if id is None: id = get_id()
	get_window().clearProperty('%s.%s' % (id, k) + k)

def parse_query(query, q={'mode': 'main'}):
	if query.startswith('?'): query = query[1:]
	queries = urlparse.parse_qs(query)
	for key in queries:
		if len(queries[key]) == 1:
			q[key] = queries[key][0]
		else:
			q[key] = queries[key]
	return q
try:
	args = parse_query(sys.argv[2])
	mode = args['mode']
except:
	args = {"mode": "main"}

def get_plugin_url(queries, addon_id=None):
	for k,v in queries.items():
		if type(v) is dict:
			queries[k] = json.dumps(v)
	try:
		query = urlencode(queries)
	except UnicodeEncodeError:
		for k in queries:
			if isinstance(queries[k], unicode):
				queries[k] = queries[k].encode('utf-8')
		query = urlencode(queries)
	addon_id = sys.argv[0] if addon_id is None else addon_id
	return addon_id + '?' + query

def get_current_view():
	window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	return window.getFocusId()

def set_default_view(view):
	set_setting('default_%s_view' % view, get_current_view())
	
def set_view(view_id, content=None):
	if content is not None:
		xbmcplugin.setContent(HANDLE_ID, content)

	xbmc.executebuiltin("Container.SetViewMode(%s)" % view_id)
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_DATE )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
	xbmcplugin.addSortMethod( handle=HANDLE_ID, sortMethod=xbmcplugin.SORT_METHOD_GENRE )

def _eod(cache_to_disc=True):
	xbmcplugin.endOfDirectory(HANDLE_ID, cacheToDisc=cache_to_disc)

def eod(view_id=None, content=None, clear_search=False):
	#from constants import DEFAULT_VIEWS
	if view_id in [DEFAULT_VIEWS.SHOWS, DEFAULT_VIEWS.SEASONS, DEFAULT_VIEWS.EPISODES]:
		content = "tvshows"
	elif view_id == DEFAULT_VIEWS.MOVIES:
		content = 'movies'
	if view_id is not None:
		set_view(view_id, content)
	_eod()

def add_menu_item(query, infolabels, total_items=0, icon='', image='', fanart='', replace_menu=True, menu=None, visible=True, format=None, in_progress=False):
	if 'display' in infolabels: infolabels['title'] = infolabels['display']
	if hasattr(visible, '__call__'):
		if visible() is False: return
	else:
		if visible is False: return
	
	if not fanart and 'fanart' in infolabels and infolabels['fanart']:
		fanart = infolabels['fanart']
	elif not fanart:
		fanart = get_path() + '/fanart.jpg'
	if format is not None:
		text = format % infolabels['title']
	else:
		text = infolabels['title']
	
	#if icon:
	#	image = vfs.join(ARTWORK, icon)
		
	listitem = xbmcgui.ListItem(text, iconImage=image, thumbnailImage=image)
	cast = infolabels.pop('cast', None)
	try:
		if cast is not None: listitem.setCast(cast)
	except: pass
	watched = False
	if 'playcount' in infolabels and int(infolabels['playcount']) > 0: watched = True 
	if not watched and in_progress:
		listitem.setProperty('totaltime', '999999')
		listitem.setProperty('resumetime', "1")
		infolabels['playcount'] = 0
	listitem.setInfo('video', infolabels)
	listitem.setProperty('IsPlayable', 'false')
	listitem.setProperty('fanart_image', fanart)
	#if menu is None:
	#	menu = ContextMenu()
	#menu.add("Addon Settings", {"mode": "addon_settings"}, script=True)
	#listitem.addContextMenuItems(menu.get(), replaceItems=replace_menu)
	plugin_url = get_plugin_url(query)
	xbmcplugin.addDirectoryItem(HANDLE_ID, plugin_url, listitem, isFolder=True, totalItems=total_items)
	