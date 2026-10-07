import wx
import os
import random
from threading import Thread


from yandex_music import Client
import nvda
import settings
import url_manager
import albums
import artists
import playlists
from player import Player
from sound_device import SoundDevice

class Albums(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.albums_page=0
		self.selected_album=0
		self.albums_results=settings.client.users_likes_albums()
		self.albums_label = wx.StaticText(panel, label='albums')
		self.alboms = wx.ListCtrl(panel, -1, (290, 130), (150, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.alboms.InsertColumn(0, 'albums')
		self.index=0

		for album in self.albums_results:
			albom_name=[]
			for artist in album.album.artists:
				albom_name.append(artist.name)
				albom_name.append(',')
			if len(albom_name)>0:
				albom_name.pop()
			else:
				albom_name.append('unnown')
			albom_name.append('-')
			albom_name.append(album.album.title)
			albom_name.append('-')
			albom_name.append(str(album.album.likes_count))
			albom_name.append('likes')
			albom_name.append(str(album.album.year))
			albom_name.append('-')
			albom_name.append(str(album.album.track_count))
			albom_name.append('tracks')
			albom_name=' '.join(albom_name)
			self.alboms.InsertItem(self.index, albom_name)
			self.index+=1

		self.alboms.Bind(wx.EVT_CHAR, self.onKeyPressAlbums)
		self.alboms.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate, id=wx.ID_ANY)
		self.alboms.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectAlbums, id=wx.ID_ANY)
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onClose(self, e):
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()

	def onKeyPressAlbums(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for album in settings.client.users_likes_albums():
				if str(album.album.id) == str(self.albums_results[self.selected_album].album.id):
					like=True
					break
			if like==False:
				nvda.say('album liked')
				settings.client.users_likes_albums_add(self.albums_results[self.selected_album].album.id)
			elif like==True:
				nvda.say('albumnot liked')
				settings.client.users_likes_albums_remove(self.albums_results[self.selected_album].album.id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='album', id=self.albums_results[self.selected_album].album.id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for album in settings.client.users_likes_albums():
				if str(self.albums_results[self.selected_album].album.id) == str(album.album.id):
					nvda.say('album is liked')
					like=True
					break
			if like==False:
				nvda.say('album is not liked')
		e.Skip()

	def onSelectAlbums(self, e):
		print(self.alboms.GetFocusedItem())
		self.selected_album = self.alboms.GetFocusedItem()

	def on_activate(self, e):
		print(self.albums_results[self.selected_album].album.title)
		Album = albums.Album(parent=self, title=self.albums_results[self.selected_album].album.title, album_id=self.albums_results[self.selected_album].album.id)
		Album.Show(True)


class Artists(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.selected_artist=0
		self.artists_page=0
		self.artists_results=settings.client.users_likes_artists()
		self.artists_label = wx.StaticText(panel, label='artists')
		self.artists = wx.ListCtrl(panel, -1, (160, 210), (210, 290), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.artists.InsertColumn(0, 'artists')
		self.index=0

		self.artists.Bind(wx.EVT_CHAR, self.onKeyPressArtists)
		self.artists.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectArtists, id=wx.ID_ANY)
		self.artists.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate, id=wx.ID_ANY)

		for artist in self.artists_results:
			artist_name=[]
			artist_name.append(artist.artist.name)
			artist_name.append('-')
			artist_name.append(str(artist.artist.counts.direct_albums))
			artist_name.append('albums')
			artist_name.append('-')
			artist_name.append(str(artist.artist.counts.tracks))
			artist_name.append('tracks')
			artist_name=' '.join(artist_name)
			self.artists.InsertItem(self.index, artist_name)
			self.index+=1

	def onSelectArtists(self, e):
		print(self.artists.GetFocusedItem())
		self.selected_artist = self.artists.GetFocusedItem()
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onClose(self, e):
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()

	def onKeyPressArtists(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for artist in settings.client.users_likes_artists():
				if str(artist.artist.id) == str(self.artists_results[self.selected_artist].id):
					like=True
					break
			if like==False:
				nvda.say('artist liked')
				settings.client.users_likes_artists_add(self.artists_results[self.selected_artist].artist.id)
			elif like==True:
				nvda.say('artist not liked')
				settings.client.users_likes_artists_remove(self.artists_results[self.selected_artist].artist.id)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='artist', id=self.artists_results[self.selected_artist].artist.id)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for artist in settings.client.users_likes_artists():
				if str(self.artists_results[self.selected_artist].id) == str(artist.artist.id):
					nvda.say('artist is liked')
					like=True
					break
			if like==False:
				nvda.say('artist is not liked')
		e.Skip()

	def on_activate(self, e):
		print(self.artists_results[self.selected_artist].artist.name)
		artist=artists.Artist(self, title=self.artists_results[self.selected_artist].artist.name, artist_id=self.artists_results[self.selected_artist].artist.id)
		artist.Show(True)


class Tracks(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.mpv = Player()
		self.stream = True
		self.selected_track=0
		self.playing_track=0
		self.tracks_page=0
		self.mpv.music.event_callback('end_file')(self.next)
		self.search_cash=os.path.join(settings.cash_folder, 'likedtrack.mp3')
		self.tracks_results = settings.client.users_likes_tracks()
		self.trecks_list = []
		self.tracks_label = wx.StaticText(panel, label='tracks')
		self.trecks = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.trecks.InsertColumn(0, 'tracks')

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

		self.trecks.Bind(wx.EVT_CHAR, self.onKeyPressTrecks)
		self.trecks.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectTracks, id=wx.ID_ANY)
		self.trecks.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activated, id=wx.ID_ANY)
		self.Bind(wx.EVT_CLOSE, self.on_close)

		self.tracks_ides_list=[]
		self.tracks_results=[]
		self.tracks_list = []
		self.index=0

		for track in settings.client.users_likes_tracks():
			self.tracks_ides_list.append(track.id)

		self.tracks_results=settings.client.tracks(self.tracks_ides_list)

		for track in self.tracks_results:
			if track.available == False:
				self.tracks_results.remove(track)

		if self.mpv.random_mode=='random':
			self.tracks_list = self.tracks_results.copy()
			random.shuffle(self.tracks_results)

		for track in self.tracks_results:
			if track.available == False:
				self.tracks_results.remove(track)
			elif track.available == True:
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

		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def onSelectTracks(self, e):
		print(self.trecks.GetFocusedItem())
		self.selected_track = self.trecks.GetFocusedItem()

	def on_activated(self, e):
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
						self.tracks_results.remove(track)
					elif track.available == True:
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
						self.tracks_results.remove(track)
					elif track.available == True:
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
			download_path=os.path.join(settings.download_path, download_name+'.mp3')
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
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_SPACE:
			download_all_thread= Thread(target=self.download_all)
			download_all_thread.start()
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

	def on_close(self, e):
		self.mpv.music.terminate()
		self.Destroy()

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
			download_path=os.path.join(settings.download_path, download_name+'.mp3')
			track.download(download_path)
		wx.MessageBox('all tracks is downloaded', 'info', wx.OK| wx.ICON_INFORMATION)

class Playlists(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.playlist_page=0
		self.selected_playlist = 0
		self.playlists_results = settings.client.users_likes_playlists()
		self.playlists_label = wx.StaticText(panel, label='playlists')
		self.playlists = wx.ListCtrl(panel, -1, (290, 130), (150, 200), wx.LC_SINGLE_SEL|wx.LC_REPORT)
		self.playlists.InsertColumn(0, 'playlists')
		self.index=0

		for pl in self.playlists_results:
			pl_name=[]
			pl_name.append(pl.playlist.title)
			pl_name.append('-')
			pl_name.append(pl.playlist.owner.name)
			pl_name.append('-')
			pl_name.append(str(pl.playlist.likes_count))
			pl_name.append('likes')
			pl_name.append('-')
			pl_name.append(str(pl.playlist.track_count))
			pl_name.append('tracks')
			pl_name=' '.join(pl_name)
			self.playlists.InsertItem(self.index, pl_name)
			self.index+=1

		self.playlists.Bind(wx.EVT_CHAR, self.onKeyPressPlaylists)
		self.playlists.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelectPlaylists, id=wx.ID_ANY)
		self.playlists.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_playlist, id=wx.ID_ANY)
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onClose(self, e):
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()

	def onSelectPlaylists(self, e):
		print(self.playlists.GetFocusedItem())
		self.selected_playlist = self.playlists.GetFocusedItem()

	def on_activate_playlist(self, e):
		print(self.playlists_results[self.selected_playlist].playlist.title)
		pl=playlists.Playlist(self, title=self.playlists_results[self.selected_playlist].playlist.title, user_id=self.playlists_results[self.selected_playlist].playlist.uid, kind=self.playlists_results[self.selected_playlist].playlist.kind)
		pl.Show(True)

	def onKeyPressPlaylists(self, e):
		if e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_L:
			like=False
			for pl in settings.client.users_likes_playlists():
				if str(pl.playlist.uid) == str(self.playlists_results[self.selected_playlist].playlist.uid):
					like=True
					break
			if like==False:
				nvda.say('playlist liked')
				settings.client.users_likes_playlists_add(playlist_ids=self.playlists_results[self.selected_playlist].playlist.title)
			elif like==True:
				nvda.say('playlistnot liked')
				settings.client.users_likes_playlists_remove(self.playlists_results.playlist[self.selected_playlists].uid)
		elif e.ControlDown() == True and e.GetKeyCode() == wx.WXK_CONTROL_C:
			url_manager.copy(type='playlist', id=self.playlists_results[self.selected_playlist].playlist.kind, id2=self.playlists_results[self.selected_playlist].playlist.owner.uid)
		elif e.GetKeyCode() == wx.WXK_F1:
			like=False
			for pl in settings.client.users_likes_playlists():
				if str(self.playlists_results[self.selected_playlist].playlist.uid) == str(pl.playlist.uid):
					nvda.say('playlist is liked')
					like=True
					break
			if like==False:
				nvda.say('playlist is not liked')
		e.Skip()
