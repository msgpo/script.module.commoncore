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
from kodi import vfs
from .addon import get_path
from .constants import *

try:
	from urllib.parse import urlencode
except ImportError:
	from urllib import urlencode

def dialog_ok(title="", m1="", m2="", m3=""):
	dialog = xbmcgui.Dialog()
	dialog.ok(title, m1, m2, m3)

def open_busy_dialog():
	xbmc.executebuiltin( "ActivateWindow(busydialog)" )

def close_busy_dialog():
	xbmc.executebuiltin( "Dialog.Close(busydialog)" )

def notify(title, message, timeout=1500, image=vfs.join(get_path(), 'icon.png')):
	cmd = "XBMC.Notification(%s, %s, %s, %s)" % (title.encode('utf-8'), message.encode('utf-8'), timeout, image)
	xbmc.executebuiltin(cmd)

def handel_error(title, message, timeout=3000):
	image=vfs.join(ARTWORK, 'error.png')
	cmd = "XBMC.Notification(%s, %s, %s, %s)" % (title.encode('utf-8'), message.encode('utf-8'), timeout, image)
	xbmc.executebuiltin(cmd)
	sys.exit()

def dialog_file_browser(title, mask='', path='/'):
	dialog = xbmcgui.Dialog()
	return dialog.browseSingle(1, title, 'files', mask, False, False, path)

def dialog_directory_browser(title, path=''):
	dialog = xbmcgui.Dialog()
	return dialog.browseSingle(0, title, path)	

def dialog_input(title, default=''):
	kb = xbmc.Keyboard(default, title, False)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
		if text != '':
			return text
	return None	

def dialog_textbox(heading, content):
		TextBox().show(heading, content)

def dialog_context(options):
	dialog = xbmcgui.Dialog()
	index = dialog.contextmenu(options)
	if index >= 0:
		return index
	else: 
		return False

def dialog_select(heading, options):
	dialog = xbmcgui.Dialog()
	index = dialog.select(heading, options)
	if index >= 0:
		return index
	else: 
		return False


class ContextMenu:
	def __init__(self):
		self.commands = []

	def add(self, text, arguments={}, script=False, visible=True, mode=False, priority=50):
		if hasattr(visible, '__call__'):
			if visible() is False: return
		else:
			if visible is False: return
		if mode: arguments['mode'] = mode	
		cmd = self._build_url(arguments, script)
		self.commands.append((text, cmd, '', priority))
	
	def _build_url(self, arguments, script):
		for k,v in arguments.items():
			if type(v) is dict:
				arguments[k] = json.dumps(v)
		try:
			plugin_url =  "%s?%s" % (sys.argv[0], urlencode(arguments))
		except UnicodeEncodeError:
			for k in arguments:
				if isinstance(arguments[k], unicode):
					arguments[k] = arguments[k].encode('utf-8')
			plugin_url =  "%s?%s" % (sys.argv[0],  urlencode(arguments))
			
		if script:
			cmd = 'XBMC.RunPlugin(%s)' % (plugin_url)
		else:
			cmd = "XBMC.Container.Update(%s)" % plugin_url
		return cmd

	def get(self):
		return sorted(self.commands, key=lambda k: k[3])	