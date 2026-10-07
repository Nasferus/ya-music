import wx
import os
import random
from threading import Thread


from yandex_music import Client
import nvda
import settings
import url_manager
from player import Player
from sound_device import SoundDevice
from radio import Radio


class Station(wx.Frame):
	def __init__(self, parent, title, id, id_for_from):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.mpv = Player()
		self.stream = True
		self.mpv.music.event_callback('end_file')(self.next)
		self.album_cash=os.path.join(settings.cash_folder, title+'-radio.mp3')
		self.tracks_label = wx.StaticText(panel, label='tracks')
		self.trecks = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.trecks.InsertColumn(0, 'tracks')
		self.index=0

		self.devices = []
		self.index_dev = 0
		self.devices_label = wx.StaticText(panel, label='output devices')
		self.list_devices = wx.ListCtrl(panel, -1, (40, 40), (140, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.list_devices.InsertColumn(0, 'devices')
		for device in self.mpv.music.audio_device_list:
			self.devices.append(SoundDevice(device["description"], device["name"]))
		for device in self.devices:
			self.list_devices.InsertItem(self.index_dev, device.name)
			self.index_dev += 1

		self.radio = Radio(settings.client)
		self.track = self.radio.start_radio(id, id_for_from)
		print("[Radio] First track is:", self.track)
		# the first track has no predecessor, so history stays empty here
		self.trecks.InsertItem(0, self.track_name())

		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.trecks.Bind(wx.EVT_CHAR, self.onKeyPressTrecks)
		self.trecks.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_track, id=wx.ID_ANY)

		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def track_name(self):
		track_name = []
		for artist in self.track.artists:
			track_name.append(artist.name)
			track_name.append(',')
		if len(track_name)>0:
			track_name.pop()
		else:
			track_name.append('unnown')
		track_name.append('-')
		track_name.append(self.track.title)
		return ' '.join(track_name)

	def set_track(self, track):
		"""Show the track in the list and start playing it.

		Used by every path that changes the current radio track: Shift+Right,
		Shift+Left, end of the track and dislike.
		"""
		self.track = track
		print(self.track.title)
		track_name = self.track_name()
		self.trecks.DeleteAllItems()
		self.trecks.InsertItem(0, track_name)
		if self.stream == False:
			self.track.download(self.album_cash)
			self.mpv.play(self.album_cash)
		else:
			self.mpv.play(self.track.get_download_info(get_direct_links=True)[0].direct_link)

	def on_activate_track(self, e):
		print(self.track.title)
		if self.stream == False:
			self.track.download(self.search_cash)
			self.mpv.play(self.search_cash)
		else:
			self.mpv.play(self.track.get_download_info(get_direct_links=True)[0].direct_link)

	def onKeyPressTrecks(self, e):
		if e.GetKeyCode() == wx.WXK_ESCAPE:
			self.mpv.pause()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='track', id=self.track.id, id2=self.track.albums[0].id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F1:
			self.mpv.change_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F2:
			self.mpv.change_volume_mode()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_D:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(track.id) == str(self.track.id):
					dislike=True
					break
			if dislike==False:
				nvda.say('track disliked')
				settings.client.users_dislikes_tracks_add(self.track.id)
				self.next_track()
			elif dislike==True:
				nvda.say('track not disliked')
				settings.client.users_dislikes_tracks_remove(self.track.id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_UP:
			self.mpv.change_volume(+5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_DOWN:
			self.mpv.change_volume(-5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
			self.mpv.seek(2)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
			self.mpv.seek(-2)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.track.id):
					like=True
					break
			if like==False:
				nvda.say('track liked')
				settings.client.users_likes_tracks_add(self.track.id)
			elif like==True:
				nvda.say('track not liked')
				settings.client.users_likes_tracks_remove(self.track.id)
		elif e.GetKeyCode() == wx.WXK_F5:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(self.track.id) == str(track.id):
					nvda.say('track is disliked')
					dislike=True
					break
			if dislike==False:
				nvda.say('track is not disliked')
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			print(self.trecks.GetItemText(0))
			download_name=self.trecks.GetItemText(0)
			download_name+='.mp3'
			if "?" in download_name:
				download_name = download_name.replace('?', '')
			if ':' in download_name:
				download_name = download_name.replace(':', '')
			if '*' in download_name:
				download_name = download_name.replace('*', '')
			if '<' in download_name:
				download_name = download_name.replace('<', '')
			if '>' in download_name:
				download_name = download_name.replace('>', '')
			if '/' in download_name:
				download_name = download_name.replace('/', '')
			if '\\' in download_name:
				download_name = download_name.replace('\\', '')
			if '|' in download_name:
				download_name = download_name.replace('|', '')
			if '"' in download_name:
				download_name = download_name.replace('"', '')
			print(download_name)
			download_path=os.path.join(settings.download_path, download_name)
			self.track.download(download_path)
			info=[]
			info.append('track : ')
			info.append(download_name)
			info.append('is downloaded')
			info= ' '.join(info)
			wx.MessageBox(info, 'info', wx.OK| wx.ICON_INFORMATION)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
			self.set_track(self.radio.play_next())
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
			if self.radio.can_play_previous():
				self.set_track(self.radio.play_previous())
			else:
				nvda.say('this is the first track')
		elif e.GetKeyCode() == wx.WXK_F1:
			nvda.say(self.track.title)
		elif e.GetKeyCode() == wx.WXK_F2:
			self.mpv.position()
		elif e.GetKeyCode() == wx.WXK_F3:
			self.mpv.volume()
		elif e.GetKeyCode() == wx.WXK_F4:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(self.track.id) == str(track.id):
					nvda.say('track is liked')
					like=True
					break
			if like==False:
				nvda.say('track is not liked')
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F5:
			if self.stream == True:
				self.stream = False
				nvda.say('.now the music is downloaded to your computer.')
			else:
				self.stream = True
				nvda.say('now the music is played directly.')
		e.Skip()

	def onClose(self, e):
		self.mpv.music.terminate()
		self.Destroy()

	def next(self, event):
		if self.mpv.music.idle_active:
			if self.mpv.mode=='track_list':
				self.set_track(self.radio.play_next())
			elif self.mpv.mode=='repeat_track':
				print(self.track.title)
				if self.stream == False:
					self.mpv.play(self.album_cash)
				else:
					self.mpv.play(self.track.get_download_info(get_direct_links=True)[0].direct_link)

	def next_track(self):
		self.set_track(self.radio.play_next())


