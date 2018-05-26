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
#import sys
#import re
#import xbmc

#import requests
#import importlib

import xbmcgui
from commoncore import kodi
from commoncore.enum import enum
from commoncore.core import format_size
from commoncore.basewindow import BaseWindow

CONTROLS = enum(CLOSE=82000, LIST=91050, TITLE=82001)
table = {9: "local.png", 8: 'hd1080.png', 7:"hd720.png", 6: "hd.png", 5: "hd.png", 4:"sd480.png", 3:"unknown.png", 2:"low.png", 1:"low.png"}
			
class StreamSelect(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self)
	
	def select_stream(self, streams):
		self.streams = streams
		return self.show()
	
	def onInit(self):
		kodi.open_busy_dialog()
		def process_streams(stream):
			icon = table[stream['quality']]
			liz = xbmcgui.ListItem(stream['title'], iconImage='definition/' + icon)
			liz.setProperty('raw_url', stream['raw_url'])
			liz.setProperty('service', stream['service'])
			liz.setProperty("host", stream['host'])
			display = []
			if 'size' in stream:
				size = format_size(stream['size'])
				if size:
					display.append('[COLOR blue]Size: ' + size + '[/COLOR]')
			if 'extension' in stream:
				if stream['extension'] is not False and stream['extension'].lower() in ['avi', 'mkv', 'mp4', 'flv']:
					display.append('[COLOR green]Ext: ' + stream['extension'] + '[/COLOR]')
			if 'x265' in stream:
				if stream['x265']:
					display.append('[COLOR darkorange]x265[/COLOR]')
			if 'hc' in stream:
				if stream['hc']:
					display.append('[COLOR olive]HC[/COLOR]')
			liz.setLabel2('  '.join(display))
			
			self.getControl(CONTROLS.LIST).addItem(liz)
		
		map(process_streams, self.streams)
		self.getControl(CONTROLS.TITLE).setLabel("Found %s stream(s)" % len(self.streams))
		self.setFocus(self.getControl(CONTROLS.LIST))
		self.getControl(CONTROLS.LIST).selectItem(0)
		kodi.close_busy_dialog()
	
	def onClick(self, controlID):
		if controlID==CONTROLS.LIST:
			index = self.getControl(CONTROLS.LIST).getSelectedPosition()
			raw_url = self.getControl(CONTROLS.LIST).getSelectedItem().getProperty("raw_url")
			service = self.getControl(CONTROLS.LIST).getSelectedItem().getProperty("service")
			from scrapecore import scrapers
			resolved_url = scrapers.get_scraper_by_name(service).resolve_url(raw_url)
			if resolved_url:
				self.return_val = resolved_url
				self.close()
			else:
				kodi.notify("Stream failed", "Select a different stream.")
				index = self.getControl(CONTROLS.LIST).removeItem(index)

		elif controlID == CONTROLS.CLOSE:
			self.close()

def select_stream(streams):
	s = StreamSelect("stream_select.xml", kodi.vfs.join("special://home/addons", "script.module.commoncore/"))
	resolved_url = s.select_stream(streams)
	kodi.log(resolved_url)
	return resolved_url

	