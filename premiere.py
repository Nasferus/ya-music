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

class Premiere(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.tracks_list = []
		self.mpv = Player()
		self.stream = True
		self.selected_track=0
		self.playing_track=0
		self.mpv.music.event_callback('end_file')(self.next)
		self.album_cash=os.path.join(settings.cash_folder, 'premiere.mp3')
		self.tracks_label = wx.StaticText(panel, label='tracks')
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

		self.PersonalPlaylistBlocks = settings.client.landing(blocks=['personalplaylists']).blocks[0]
		self.premierepl = next(
			x.data.data for x in self.PersonalPlaylistBlocks.entities if x.data.data.generated_playlist_type == 'recentTracks'
		)
		self.playlist = settings.client.users_playlists(self.premierepl.kind, self.premierepl.uid)
		self.tracks_results=self.playlist.tracks
		self.tracks_ides_list=[]

		for track in self.tracks_results:
			self.tracks_ides_list.append(track.id)

		self.tracks_results=settings.client.tracks(self.tracks_ides_list)

		if self.mpv.random_mode=='random':
			self.tracks_list = self.tracks_results.copy()
			random.shuffle(self.tracks_results)

		for track in self.tracks_results:
			if track.available == False:
				continue
			track_name= []
			for artist in track.artists:
				track_name.append(artist.name)
				track_name.append(',')
			if len(track_name)>0:
				track_name.pop()
			else:
				track_name.append('unnown')
			track_name.append('-')
			track_name.append(track.title)
			track_name = ' '.join(track_name)
			self.trecks.InsertItem(self.index, track_name)
			self.index+=1

		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.trecks.Bind(wx.EVT_CHAR, self.onKeyPressTrecks)
		self.trecks.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectTracks, id=wx.ID_ANY)
		self.trecks.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_track, id=wx.ID_ANY)

		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def onSelectTracks(self, e):
		print(self.trecks.GetFocusedItem())
		self.selected_track=self.trecks.GetFocusedItem()

	def on_activate_track(self, e):
		print(self.tracks_results[self.selected_track].title)
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.album_cash)
			self.mpv.play(self.album_cash)
		else:
			self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def onKeyPressTrecks(self, e):
		if e.GetKeyCode() == wx.WXK_ESCAPE:
			self.mpv.pause()
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='track', id=self.tracks_results[self.selected_track].id, id2=self.tracks_results[self.selected_track].albums[0].id)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F1:
			self.mpv.change_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F2:
			self.mpv.change_volume_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F3:
			self.mpv.change_random_mode()
			index=0
			self.trecks.DeleteAllItems()
			if self.mpv.random_mode== 'random':
				if len(self.tracks_results)>0:
					self.tracks_list = self.tracks_results.copy()
					random.shuffle(self.tracks_results)
				for track in self.tracks_results:
					if track.available == False:
						continue
					track_name= []
					for artist in track.artists:
						track_name.append(artist.name)
						track_name.append(',')
					if len(track_name)>0:
						track_name.pop()
					else:
						track_name.append('unnown')
					track_name.append('-')
					track_name.append(track.title)
					track_name = ' '.join(track_name)
					self.trecks.InsertItem(index, track_name)
					index+=1
			elif self.mpv.random_mode == 'list':
				print(len(self.tracks_list))
				self.tracks_results = self.tracks_list.copy()
				for track in self.tracks_results:
					if track.available == False:
						continue
					track_name= []
					for artist in track.artists:
						track_name.append(artist.name)
						track_name.append(',')
					if len(track_name)>0:
						track_name.pop()
					else:
						track_name.append('unnown')
					track_name.append('-')
					track_name.append(track.title)
					track_name = ' '.join(track_name)
					self.trecks.InsertItem(index, track_name)
					index+=1
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F5:
			if self.stream == True:
				self.stream = False
				nvda.say('.now the music is downloaded to your computer.')
			else:
				self.stream = True
				nvda.say('now the music is played directly.')
		elif e.ShiftDown() == True and e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(track.id) == str(self.tracks_results[self.playing_track].id):
					like=True
					break
			if like==False:
				nvda.say('track liked')
				settings.client.users_likes_tracks_add(self.tracks_results[self.playing_track].id)
			elif like==True:
				nvda.say('track not liked')
				settings.client.users_likes_tracks_remove(self.tracks_results[self.playing_track].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_D:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(track.id) == str(self.tracks_results[self.playing_track].id):
					dislike=True
					break
			if dislike==False:
				nvda.say('track disliked')
				settings.client.users_dislikes_tracks_add(self.tracks_results[self.playing_track].id)
				self.next_track()
			elif dislike==True:
				nvda.say('track not disliked')
				settings.client.users_dislikes_tracks_remove(self.tracks_results[self.playing_track].id)
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
				if str(track.id) == str(self.tracks_results[self.selected_track].id):
					like=True
					break
			if like==False:
				nvda.say('track liked')
				settings.client.users_likes_tracks_add(self.tracks_results[self.selected_track].id)
			elif like==True:
				nvda.say('track not liked')
				settings.client.users_likes_tracks_remove(self.tracks_results[self.selected_track].id)
		elif e.GetKeyCode() == wx.WXK_F5:
			dislike=False
			for track in settings.client.users_dislikes_tracks():
				if str(self.tracks_results[self.selected_track].id) == str(track.id):
					nvda.say('track is disliked')
					dislike=True
					break
			if dislike==False:
				nvda.say('track is not disliked')
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			print(self.trecks.GetItemText(self.selected_track))
			download_name=self.trecks.GetItemText(self.selected_track)
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
			self.tracks_results[self.selected_track].download(download_path)
			info=[]
			info.append('track : ')
			info.append(download_name)
			info.append('is downloaded')
			info= ' '.join(info)
			wx.MessageBox(info, 'info', wx.OK| wx.ICON_INFORMATION)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
				self.trecks.Focus(self.playing_track-1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.album_cash)
					self.mpv.play(self.album_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
				self.trecks.Focus(self.playing_track+1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.album_cash)
					self.mpv.play(self.album_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.GetKeyCode() == wx.WXK_F1:
			nvda.say(self.tracks_results[self.playing_track].title)
		elif e.GetKeyCode() == wx.WXK_F2:
			self.mpv.position()
		elif e.GetKeyCode() == wx.WXK_F3:
			self.mpv.volume()
		elif e.GetKeyCode() == wx.WXK_F4:
			like=False
			for track in settings.client.users_likes_tracks():
				if str(self.tracks_results[self.playing_track].id) == str(track.id):
					nvda.say('track is liked')
					like=True
					break
			if like==False:
				nvda.say('track is not liked')

		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			download_all_thread= Thread(target=self.download_all)
			download_all_thread.start()
		e.Skip()

	def onClose(self, e):
		self.mpv.music.terminate()
		self.Destroy()

	def next(self, event):
		if self.mpv.music.idle_active:
			if self.mpv.mode=='track_list':
				self.trecks.Focus(self.playing_track+1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.album_cash)
					self.mpv.play(self.album_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
			elif self.mpv.mode=='repeat_track':
				print(self.tracks_results[self.playing_track].title)
				if self.stream == False:
					self.mpv.play(self.album_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def next_track(self):
		self.trecks.Focus(self.playing_track+1)
		self.selected_track=self.trecks.GetFocusedItem()
		print(self.tracks_results[self.selected_track].title)
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.album_cash)
			self.mpv.play(self.album_cash)
		else:
			self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def download_all(self):
		for track in self.tracks_results:
			track_name= []
			for artist in track.artists:
				track_name.append(artist.name)
				track_name.append(',')
			if len(track_name)>0:
				track_name.pop()
			else:
				track_name.append('unnown')
			track_name.append('-')
			track_name.append(track.title)
			track_name = ' '.join(track_name)
			track_name+='.mp3'
			download_name = track_name
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
			download_path=os.path.join(settings.download_path, track_name)
			track.download(download_path)
		wx.MessageBox('all tracks is downloaded', 'info', wx.OK| wx.ICON_INFORMATION)
