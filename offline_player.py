import wx
import sys
import os
import pathlib
from os import path
import random

import mpv
from player import Player
from sound_device import SoundDevice

class Window(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.Show(True)
		self.mpv = Player()
		self.mpv.music.event_callback('end_file')(self.next)
		self.fdir=''
		self.files = []
		self.norm_files = []

		self.mpause=False
		self.playing_track = 0
		self.devices = []
		self.index_dev = 0

		self.tracks_label = wx.StaticText(panel, label='tracks')
		self.list = wx.ListCtrl(panel, -1, (20, 20), (80, 120), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.devices_label = wx.StaticText(panel, label='output devices')
		self.list_devices = wx.ListCtrl(panel, -1, (40, 40), (140, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.list.SetFocus()
		self.list.InsertColumn(0, 'audios')
		self.list_devices.InsertColumn(0, 'devices')

		for device in self.mpv.music.audio_device_list:
			self.devices.append(SoundDevice(device["description"], device["name"]))

		for device in self.devices:
			self.list_devices.InsertItem(self.index_dev, device.name)
			self.index_dev += 1

		menu = wx.Menu() # создаём экземпляр меню
		openItem = menu.Append(wx.ID_ANY, "Open", "Push the button to open the file")
		exitItem = menu.Append(wx.ID_EXIT,"Exit","Push the button to leave this application") # а как ещё?
		bar = wx.MenuBar() # создаём рабочую область для меню
		bar.Append(menu,"&File") # добавляем пункт меню
		self.SetMenuBar(bar) # указываем, что это меню надо показать в нашей форме
		self.Bind(wx.EVT_MENU, self.On_Open, openItem)
		self.Bind(wx.EVT_MENU, self.On_Exit, exitItem)
		self.list.Bind(wx.EVT_CHAR, self.onKeyPress)
		self.list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activated)
		self.list_devices.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_devices_activated)

	def on_activated(self, e):
		print(self.list.GetItemText(self.list.GetFocusedItem()))
		self.file= os.path.join(self.fdir, self.list.GetItemText(self.list.GetFocusedItem()))
		self.playing_track = self.list.GetFocusedItem()
		self.mpv.play(self.file)

	def on_devices_activated(self, e):
		self.mpv.music.audio_device = self.devices[self.list_devices.GetFocusedItem()].id

	def onKeyPress(self, e):
		if e.GetKeyCode() == wx.WXK_ESCAPE:
			self.mpv.pause()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F1:
			self.mpv.change_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F2:
			self.mpv.change_volume_mode()
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_F3:
			self.mpv.change_random_mode()
			index=0
			self.list.DeleteAllItems()
			if self.mpv.random_mode== 'random':
				random.shuffle(self.files)
				print(len(self.files))
				for file in self.files:
					self.list.InsertItem(index, file)
					index+=1
			elif self.mpv.random_mode == 'list':
				for file in self.norm_files:
					self.list.InsertItem(index, file)
					index+=1
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_UP:
			self.mpv.change_volume(+5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_DOWN:
			self.mpv.change_volume(-5)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
			self.mpv.seek(2)
		elif e.AltDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
			self.mpv.seek(-2)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_LEFT:
				self.list.Focus(self.playing_track-1)
				self.playing_track = self.list.GetFocusedItem()
				print(self.list.GetItemText(self.list.GetFocusedItem()))
				self.file = os.path.join(self.fdir, self.list.GetItemText(self.list.GetFocusedItem()))
				self.mpv.play(self.file)
		elif e.ShiftDown() == True and e.GetKeyCode() == wx.WXK_RIGHT:
				self.list.Focus(self.playing_track+1)
				self.playing_track = self.list.GetFocusedItem()
				print(self.list.GetItemText(self.list.GetFocusedItem()))
				self.file = os.path.join(self.fdir, self.list.GetItemText(self.list.GetFocusedItem()))
				self.mpv.play(self.file)
		elif e.GetKeyCode() == wx.WXK_F1:
			self.mpv.position()
		elif e.GetKeyCode() == wx.WXK_F2:
			self.mpv.volume()
		e.Skip()

	def On_Open(self, e):
		index=0
		dlg = wx.DirDialog(self, "Выбор директории...", "", wx.DD_DEFAULT_STYLE)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			self.fdir = dlg.GetPath()
			print("Выбран каталог: "+self.fdir)
			os.chdir(self.fdir)
			print(os.getcwd())
			self.files=[]
			self.norm_files = []
			self.list.DeleteAllItems()
			for f in os.listdir():
				if os.path.isfile(f) and f.endswith('.mp3'):
					self.files.append(f)
					self.norm_files.append(f)
			self.SetTitle("offline player - "+self.fdir) # меняем заголовок окна
			self.fdir=pathlib.Path(self.fdir)
			for file in self.files:
				self.list.InsertItem(index, file)
				index+=1

	def next(self, event):
		if self.mpv.music.idle_active:
			if self.mpv.mode=='track_list':
				self.list.Focus(self.playing_track+1)
				self.playing_track = self.list.GetFocusedItem()
				print(self.list.GetItemText(self.list.GetFocusedItem()))
				self.file = os.path.join(self.fdir, self.list.GetItemText(self.list.GetFocusedItem()))
				self.mpv.play(self.file)
			elif self.mpv.mode=='repeat_track':
				self.mpv.play(self.file)

	def On_Exit(self, e):
		sys.exit()

if __name__=='__main__':
	app = wx.App()
	wnd = Window(None, title='Kplayer')
	app.MainLoop()
