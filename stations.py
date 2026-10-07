import wx
import os
import random
from threading import Thread

from yandex_music import Client
import settings
from radio import Radio
import station

class Stations(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.stations_results = settings.client.rotor_stations_list()
		self.stations_label = wx.StaticText(panel, label='stations')
		self.stations = wx.ListCtrl(panel, -1, (40, 40), (140, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.stations.InsertColumn(0, 'stations')
		self.station_index = 0
		for _station in self.stations_results:
			self.stations.InsertItem(self.station_index, _station.station.name)
			self.station_index+=1

		self.re_stations_results = settings.client.rotor_stations_dashboard().stations
		self.re_stations_label = wx.StaticText(panel, label='recommended stations')
		self.re_stations = wx.ListCtrl(panel, -1, (40, 40), (140, 200), wx.LC_REPORT|wx.LC_SINGLE_SEL)
		self.re_stations.InsertColumn(0, 'stations')
		self.re_station_index = 0

		for _station in self.re_stations_results:
			self.re_stations.InsertItem(self.re_station_index, _station.station.name)
			self.re_station_index+=1

		self.stations.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_station, id=wx.ID_ANY)
		self.re_stations.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_activate_re_station, id=wx.ID_ANY)

		self.Bind(wx.EVT_CLOSE, self.onClose)

	def on_activate_station(self, e):
		radio = station.Station(self, title=self.stations_results[self.stations.GetFocusedItem()].station.name, id=f'{self.stations_results[self.stations.GetFocusedItem()].station.id.type}:{self.stations_results[self.stations.GetFocusedItem()].station.id.tag}', id_for_from=self.stations_results[self.stations.GetFocusedItem()].station.id_for_from)
		radio.Show(True)

	def on_activate_re_station(self, e):
		radio = station.Station(self, title=self.re_stations_results[self.re_stations.GetFocusedItem()].station.name, id=f'{self.re_stations_results[self.re_stations.GetFocusedItem()].station.id.type}:{self.re_stations_results[self.re_stations.GetFocusedItem()].station.id.tag}', id_for_from=self.re_stations_results[self.re_stations.GetFocusedItem()].station.id_for_from)
		radio.Show(True)

	def onClose(self, e):
		childrens = self.GetChildren()
		for children in childrens:
			if children.Name == 'panel':
				continue
			children.onClose(wx.CloseEvent)
		self.Destroy()