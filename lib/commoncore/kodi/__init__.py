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

import importlib
__all__ = ['addon', 'constants', 'enum', 'formating', 'logger', 'playback', 'runner', 'ui', 'strings', 'vfs']
for name in __all__:
	""" loop through each module in __all__
	    import them serially and copy their contents to globals
	"""
	mod = importlib.import_module("{}.{}".format(__name__, name))
	if "__all__" in mod.__dict__:
		names = mod.__dict__["__all__"]
	else:
		names = [x for x in mod.__dict__ if not x.startswith("_")]
	globals().update({k: getattr(mod, k) for k in names})
