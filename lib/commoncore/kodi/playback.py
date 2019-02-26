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

import json
import xbmc
import xbmcplugin
import xbmcgui
from .constants import *
from .runner import args
from .addon import get_property, set_property, go_to_url

def play_stream(url, metadata={"poster": "", "title": "", "resume_point": ""}):
	set_property('core.playing', "true", 'service.core.playback')
	if url.startswith("playlist://"):
		li = eval(url[11:])
		plst = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
		plst.clear()
		xbmc.sleep(200)
		for l in li:
			index = li.index(l)
			liz = xbmcgui.ListItem(metadata['title'], path=l)
			plst.add(l, liz, index)
			if index == 0: xbmcplugin.setResolvedUrl(HANDLE_ID, True, liz)
		plst.unshuffle()
	else:
		listitem = xbmcgui.ListItem(metadata['title'], iconImage=metadata['poster'], thumbnailImage=metadata['poster'], path=url)
		listitem.setPath(url)
		listitem.setInfo("video", metadata)
		listitem.setProperty('IsPlayable', 'true')
		resume_point = check_resume_point()
		
		if resume_point:
			listitem.setProperty('totaltime', '999999')
			listitem.setProperty('resumetime', str(resume_point))
		if HANDLE_ID > -1:
			xbmcplugin.setResolvedUrl(HANDLE_ID, True, listitem)
		else:
			xbmc.Player().play(url, listitem)
	while get_property('core.playing', 'service.core.playback'):
		xbmc.sleep(100)
	_on_playback_stop()

def set_playback_info(infoLabel):
	set_property('core.infolabel', json.dumps(infoLabel), "service.core.playback")

def get_playback_times():
	#try:
	percent = int(get_property('core.percent', 'service.core.playback'))
	current_time = get_property('core.current_time', 'service.core.playback')
	total_time = get_property('core.total_time', 'service.core.playback')
	return current_time, total_time, percent
	#except:
	#	return 0,0,0
	
def check_resume_point():
	if 'media' in args and 'trakt_id' in args:
		import coreplayback
		return coreplayback.check_resume_point(args['media'], args['trakt_id'])
	return False
		

def on_playback_stop():
	pass

def _on_playback_stop():
	on_playback_stop()
	hash = get_property('Playback.Hash')
	if hash:
		from scrapecore.scrapecore import delete_torrent
		resolver = get_property('Playback.Resolver')
		id = get_property('Playback.Id')
		delete_torrent(resolver, hash, id)
		set_property('Playback.Hash', '')
		set_property('Playback.Resolver', '')
		set_property('Playback.Id', '')
	
	if get_setting('refresh_onstop') == 'true': 
		go_to_url(get_property('last.plugin.url'))