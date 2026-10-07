import wx
import os
import random
from threading import Thread


from yandex_music import Client
import nvda
import settings
import url_manager
import albums
from player import  Player
from sound_device import SoundDevice

class Artist(wx.Frame):
	def __init__(self, parent, title, artist_id=0):
		wx.Frame.__init__(self, parent, title = title+' - artist', size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.mpv = Player()
		self.stream = True
		self.artist=settings.client.artists(artist_id)[0]
		self.tracks_page=0
		self.albums_page=0
		self.artist_id=artist_id
		self.selected_track=0
		self.playing_track=0
		self.selected_album=0
		self.search_cash=os.path.join(settings.cash_folder, title+'.mp3')

		self.mpv.music.event_callback('end_file')(self.next)

		self.tracks_results = settings.client.artists_tracks(artist_id=artist_id)
		self.albums_results=settings.client.artists_direct_albums(artist_id=artist_id)
		self.tracks_list = []

		self.albums_label = wx.StaticText(panel, label='albums')
		self.alboms = wx.ListCtrl(panel, -1, (290, 130), (150, 200), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.alboms.SetFocus()
		self.tracks_label = wx.StaticText(panel, label='tracks')
		self.trecks = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.trecks.InsertColumn(0, 'tracks')
		self.alboms.InsertColumn(0, 'albums')
		index_tre = 0
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

		for device in self.devices:
			self.list_devices.InsertItem(self.index_dev, device.name)
			self.index_dev += 1


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
			self.trecks.InsertItem(index_tre, track_name)
			index_tre+=1

		for album in self.albums_results:
			albom_name=[]
			for artist in album.artists:
				albom_name.append(artist.name)
				albom_name.append(',')
			if len(albom_name)>0:
				albom_name.pop()
			else:
				albom_name.append('unnown')
			albom_name.append('-')
			albom_name.append(album.title)
			albom_name.append('-')
			albom_name.append(str(album.likes_count))
			albom_name.append('likes')
			albom_name.append(str(album.year))
			albom_name.append('-')
			albom_name.append(str(album.track_count))
			albom_name.append('tracks')
			albom_name=' '.join(albom_name)
			self.alboms.InsertItem(self.index, albom_name)
			self.index+=1



		self.trecks.Bind(wx.EVT_CHAR, self.onKeyPressTrecks)
		self.trecks.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectTracks, id=wx.ID_ANY)
		self.trecks.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_track, id=wx.ID_ANY)

		self.alboms.Bind(wx.EVT_CHAR, self.onKeyPressAlbums)
		self.alboms.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectAlbums, id=wx.ID_ANY)
		self.alboms.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_album, id=wx.ID_ANY)

		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onClose(self, e):
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def onSelectAlbums(self, e):
		print(self.alboms.GetFocusedItem())
		self.selected_album=self.alboms.GetFocusedItem()

	def on_activate_album(self, e):
		print(self.albums_results[self.selected_album].title)
		Album = albums.Album(parent=self, title=self.albums_results[self.selected_album].title, album_id=self.albums_results[self.selected_album].id)
		Album.Show(True)

	def onKeyPressAlbums(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for album in settings.client.users_likes_albums():
				if str(album.album.id) == str(self.albums_results[self.selected_album].id):
					like=True
					break
			if like==False:
				nvda.say('album liked')
				settings.client.users_likes_albums_add(self.albums_results[self.selected_album].id)
			elif like==True:
				nvda.say('albumnot liked')
				settings.client.users_likes_albums_remove(self.albums_results[self.selected_album].id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='album', id=self.albums_results[self.selected_album].id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for album in settings.client.users_likes_albums():
				if str(self.albums_results[self.selected_album].id) == str(album.album.id):
					nvda.say('album is liked')
					like=True
					break
			if like==False:
				nvda.say('album is not liked')
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.alboms.DeleteAllItems()
			self.index=0
			self.albums_page+=1
			self.albums_results = settings.client.artists_direct_albums(artist_id=self.artist_id, page=self.albums_page)
			for album in self.albums_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.likes_count))
				albom_name.append('likes')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('tracks')
				albom_name=' '.join(albom_name)
				self.alboms.InsertItem(self.index, albom_name)
				self.index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.alboms.DeleteAllItems()
			self.index=0
			self.albums_page-=1
			self.albums_results = settings.client.artists_direct_albums(artist_id=self.artist_id, page=self.albums_page)
			for album in self.albums_results:
				albom_name=[]
				for artist in album.artists:
					albom_name.append(artist.name)
					albom_name.append(',')
				if len(albom_name)>0:
					albom_name.pop()
				else:
					albom_name.append('unnown')
				albom_name.append('-')
				albom_name.append(album.title)
				albom_name.append('-')
				albom_name.append(str(album.likes_count))
				albom_name.append('likes')
				albom_name.append(str(album.year))
				albom_name.append('-')
				albom_name.append(str(album.track_count))
				albom_name.append('tracks')
				albom_name=' '.join(albom_name)
				self.alboms.InsertItem(self.index, albom_name)
				self.index+=1
		e.Skip()

	def onSelectTracks(self, e):
		print(self.trecks.GetFocusedItem())
		self.selected_track=self.trecks.GetFocusedItem()

	def on_activate_track(self, e):
		print(self.tracks_results[self.selected_track].title)
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.search_cash)
			self.mpv.play(self.search_cash)
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
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			download_all_thread= Thread(target=self.download_all)
			download_all_thread.start()
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
					self.tracks_results[self.selected_track].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
				self.trecks.Focus(self.playing_track+1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.search_cash)
					self.mpv.play(self.search_cash)
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
		elif e.GetKeyCode() == wx.WXK_PAGEDOWN:
			self.trecks.DeleteAllItems()
			self.playing_track=0
			index=0
			self.tracks_page+=1
			self.tracks_results= settings.client.artists_tracks(artist_id=self.artist_id, page=self.tracks_page)
			if self.mpv.random_mode=='random':
				self.tracks_list = self.tracks_results.copy()
				random.shuffle(self.tracks_results)
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
				self.trecks.InsertItem(index, track_name)
				index+=1
		elif e.GetKeyCode() == wx.WXK_PAGEUP:
			self.trecks.DeleteAllItems()
			self.playing_track=0
			index=0
			self.tracks_page-=1
			self.tracks_results= settings.client.artists_tracks(artist_id=self.artist_id, page=self.tracks_page)
			if self.mpv.random_mode=='random':
				self.tracks_list = self.tracks_results.copy()
				random.shuffle(self.tracks_results)
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
				self.trecks.InsertItem(index, track_name)
				index+=1
		e.Skip()


	def next(self, event):
		if self.mpv.music.idle_active:
			if self.mpv.mode=='track_list':
				self.trecks.Focus(self.playing_track+1)
				self.selected_track=self.trecks.GetFocusedItem()
				print(self.tracks_results[self.selected_track].title)
				self.playing_track=self.selected_track
				if self.stream == False:
					self.tracks_results[self.selected_track].download(self.search_cash)
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)
			elif self.mpv.mode=='repeat_track':
				print(self.tracks_results[self.playing_track].title)
				if self.stream == False:
					self.mpv.play(self.search_cash)
				else:
					self.mpv.play(self.tracks_results[self.selected_track].get_download_info(get_direct_links=True)[0].direct_link)

	def next_track(self):
		self.trecks.Focus(self.playing_track+1)
		self.selected_track=self.trecks.GetFocusedItem()
		print(self.tracks_results[self.selected_track].title)
		self.playing_track=self.selected_track
		if self.stream == False:
			self.tracks_results[self.selected_track].download(self.search_cash)
			self.mpv.play(self.search_cash)
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
