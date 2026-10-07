import wx
import sys
import os
import shutil
import requests

from yandex_music import Client
import json
import search
import user
import settings
import stations
import dailyplaylist
import premiere
import dejavu
import missedlikes
import alice
import liked_collections
import offline_player


# yandex-music 2.2.0: User.login is a required dataclass field, but the API does
# not return `login` inside playlist.made_for.user_info, while MadeFor.de_json
# calls User.de_json on it unconditionally -> TypeError on every personal
# playlist (Daily, Premiere, Dejavu, Missed likes, Alice). Patch the model.
def _patch_yandex_music_user_login():
	try:
		from yandex_music.playlist.user import User as _YmUser
	except Exception:
		return
	if getattr(_YmUser, '_wam_login_patched', False):
		return
	_orig_de_json = _YmUser.de_json.__func__

	def _de_json(cls, data, client=None):
		if isinstance(data, dict) and not data.get('login'):
			data = dict(data)
			data['login'] = ''
		return _orig_de_json(cls, data, client)

	_YmUser.de_json = classmethod(_de_json)
	_YmUser._wam_login_patched = True


_patch_yandex_music_user_login()

settings.folder_check()
settings.cash_check()
settings.music_check()
settings.config_check()

with open(settings.config_path, "r") as read_file:
	config = json.load(read_file)
	u_token = config['general']['token']
	u_name = config['general']['user_name']
	u_password = config['general']['password']
CLIENT_ID = "23cabbbdc6cd418abb4b39c32c41195d"
CLIENT_SECRET = "53bc75238f0c4d08a118e51fe9203300"
USER_AGENT = "Yandex-Music-API"
HEADERS = {
    "X-Yandex-Music-Client": "YandexMusicAndroid/23020251",
    "USER_AGENT": USER_AGENT,
}
url = "https://oauth.yandex.ru/token"


def get_token(
    username, password, grant_type="password", x_captcha_answer=None, x_captcha_key=None
):
    data = {
        "grant_type": grant_type,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": username,
        "password": password,
    }
    if x_captcha_answer and x_captcha_key:
        data.update(
            {"x_captcha_answer": x_captcha_answer, "x_captcha_key": x_captcha_key}
        )
    try:
        resp = requests.request("post", url, data=data, headers=HEADERS)
    except requests.RequestException as e:
        raise NetworkError(e)
    if not (200 <= resp.status_code <= 299):
        raise SystemError("Error")
    json_data = json.loads(resp.content.decode("utf-8"))
    return json_data["access_token"]

class LoginDialog(wx.Dialog):
    """
   Class to define login dialog
    """

    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Login")
        self.logged_in = True

        token_sizer = wx.BoxSizer(wx.HORIZONTAL)

        token_lbl = wx.StaticText(self, label="Token:")
        token_sizer.Add(token_lbl, 0, wx.ALL|wx.CENTER, 5)
        self.token = wx.TextCtrl(self)
        token_sizer.Add(self.token, 0, wx.ALL, 5)

        # user info
        user_sizer = wx.BoxSizer(wx.HORIZONTAL)

        user_lbl = wx.StaticText(self, label="Username:")
        user_sizer.Add(user_lbl, 0, wx.ALL|wx.CENTER, 5)
        self.user = wx.TextCtrl(self)
        user_sizer.Add(self.user, 0, wx.ALL, 5)

        # pass info
        p_sizer = wx.BoxSizer(wx.HORIZONTAL)

        p_lbl = wx.StaticText(self, label="Password:")
        p_sizer.Add(p_lbl, 0, wx.ALL|wx.CENTER, 5)
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD|wx.TE_PROCESS_ENTER)
        self.password.Bind(wx.EVT_TEXT_ENTER, self.onLogin)
        p_sizer.Add(self.password, 0, wx.ALL, 5)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(token_sizer, 0, wx.ALL, 5)
        main_sizer.Add(user_sizer, 0, wx.ALL, 5)
        main_sizer.Add(p_sizer, 0, wx.ALL, 5)

        btn = wx.Button(self, label="Login")
        btn.Bind(wx.EVT_BUTTON, self.onLogin)
        main_sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)

        self.SetSizer(main_sizer)

    def onLogin(self, event):
        """
        Check credentials and login
        """
        token = self.token.GetValue()
        user_name = self.user.GetValue()
        user_password = self.password.GetValue()
        self.logged_in = True
        print(token, user_name, user_password)
        if len(token) > 0:
            settings.client = settings.login(token)
        else:
            try:
                token = get_token(user_name, user_password)
                print(token)
                settings.client = settings.login(token)
            except Exception as ept:
                print(ept)
                self.logged_in = False
        if self.logged_in == True:
            with open(settings.config_path) as f:
                config = json.load(f)
                config['general']['token'] = token
                config['general']['user_name'] = user_name
                config['general']['password'] = user_password
            with open(settings.config_path, 'w') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            self.Close()

class Window(wx.Frame):
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title = title, size = (300,250))
		panel = wx.Panel(self, wx.ID_ANY)
		self.Show(True)
		files=()
		self.listBox = wx.ListBox(panel, -1, (20, 20), (80, 120), files, wx.LB_SINGLE)

		self.listBox.SetSelection(-1)
		if u_token != '':
			settings.client = settings.login(u_token)
		elif (u_name or u_password) == '':
			dlg = LoginDialog()
			dlg.ShowModal()
			authenticated = dlg.logged_in
			dlg.Destroy()
			if not authenticated:
				self.Close()

		menu = wx.Menu() # создаём экземпляр меню
		collection_menu=wx.Menu()
		offline_menu=wx.Menu()

		loginItem = menu.Append(wx.ID_ANY, "Login", "Push the button to login")
		searchItem = menu.Append(wx.ID_ANY, "Search", "Push the button to search")
		u_searchItem = menu.Append(wx.ID_ANY, "User search", "Push the button to search")
		radioItem = menu.Append(wx.ID_ANY, "stations", "Push the button to open")
		dailyItem = menu.Append(wx.ID_ANY, "Daily Playlist", "Push the button to open")
		premiereItem = menu.Append(wx.ID_ANY, "premiere", "Push the button to open")
		dejavuItem = menu.Append(wx.ID_ANY, "Deja vu", "Push the button to open")
		missedlikesItem = menu.Append(wx.ID_ANY, "Missed likes", "Push the button to open")
		aliceItem = menu.Append(wx.ID_ANY, "playlist with alice", "Push the button to open")
		exitItem = menu.Append(wx.ID_EXIT,"Exit","Push the button to leave this application") # а как ещё?

		tracksItem = collection_menu.Append(wx.ID_ANY, "tracks", "Push the button to open liked tracks")
		albumsItem = collection_menu.Append(wx.ID_ANY, "albums", "Push the button to open liked albums")
		artistsItem = collection_menu.Append(wx.ID_ANY, "artists", "Push the button to open liked artists")
		playlistsItem = collection_menu.Append(wx.ID_ANY, "playlists", "Push the button to open liked playlists")

		offlinePlayerItem = offline_menu.Append(wx.ID_ANY, "offline player", "Push the button to open offline player")

		bar = wx.MenuBar() # создаём рабочую область для меню
		bar.Append(menu,"&Main") # добавляем пункт меню
		bar.Append(offline_menu, "&Offline player") # добавляем пункт меню
		bar.Append(collection_menu, "&Collection") # добавляем пункт меню
		self.SetMenuBar(bar) # указываем, что это меню надо показать в нашей форме

		self.Bind(wx.EVT_CLOSE, self.onClose)

		self.Bind(wx.EVT_MENU, self.On_Login, loginItem)
		self.Bind(wx.EVT_MENU, self.on_Search, searchItem)
		self.Bind(wx.EVT_MENU, self.on_User_Search, u_searchItem)
		self.Bind(wx.EVT_MENU, self.on_Radio, radioItem)
		self.Bind(wx.EVT_MENU, self.on_Daily, dailyItem)
		self.Bind(wx.EVT_MENU, self.on_Premiere, premiereItem)
		self.Bind(wx.EVT_MENU, self.on_Dejavu, dejavuItem)
		self.Bind(wx.EVT_MENU, self.on_MissedLikes, missedlikesItem)
		self.Bind(wx.EVT_MENU, self.on_Alice, aliceItem)
		self.Bind(wx.EVT_MENU, self.On_Exit, exitItem)

		self.Bind(wx.EVT_MENU, self.on_tracks, tracksItem)
		self.Bind(wx.EVT_MENU, self.on_albums, albumsItem)
		self.Bind(wx.EVT_MENU, self.on_artists, artistsItem)
		self.Bind(wx.EVT_MENU, self.on_playlists, playlistsItem)

		self.Bind(wx.EVT_MENU, self.on_offline_player, offlinePlayerItem)

	def On_Login(self, e):
			dlg = LoginDialog()
			dlg.ShowModal()
			authenticated = dlg.logged_in
			dlg.Destroy()
			if not authenticated:
				self.Close()

	def on_Search(self, e):
		searches = search.SearchWindow(self, 'search')
		searches.Show(True)

	def on_User_Search(self, e):
		u_search = user.SearchWindow(self, 'users search')

	def on_Radio(self, e):
		Radio = stations.Stations(self, title='Stations')
		Radio.Show(True)

	def on_Daily(self, e):
		Dpl = dailyplaylist.DailyPlaylist(self, title='Daily Playlist')
		Dpl.Show(True)

	def on_Premiere(self, e):
		Prem = premiere.Premiere(self, title='premiere')
		Prem.Show(True)

	def on_Dejavu(self, e):
		dejavupl = dejavu.Dejavu(self, title='Deja vu')
		dejavupl.Show(True)

	def on_MissedLikes(self, e):
		missedlikespl = missedlikes.MissedLikes(self, title='Missed likes')
		missedlikespl.Show(True)

	def on_Alice(self, e):
		alicepl = alice.Alice(self, title='Playlist with alice')
		alicepl.Show(True)

	def On_Exit(self, e):
		sys.exit()

	def on_tracks(self, e):
		tracks= liked_collections.Tracks(self, title='my liked tracks')
		tracks.Show(True)

	def on_albums(self, e):
		albums= liked_collections.Albums(self, title='my liked albums')
		albums.Show(True)

	def on_artists(self, e):
		artists=liked_collections.Artists(self, title='my liked artists')
		artists.Show(True)

	def on_playlists(self, e):
		pl=liked_collections.Playlists(self, title='my liked playlists')
		pl.Show(True)

	def on_offline_player(self, e):
		oplayer=offline_player.Window(self, title='offline player')
		oplayer.Show(True)

	def onClose(self, e):
		folder = settings.cash_folder
		for filename in os.listdir(folder):
			file_path = os.path.join(folder, filename)
			try:
				if os.path.isfile(file_path) or os.path.islink(file_path):
					os.unlink(file_path)
				elif os.path.isdir(file_path):
					shutil.rmtree(file_path)
			except Exception as e:
				print('Failed to delete %s. Reason: %s' % (file_path, e))
		self.Destroy()


app = wx.App()
wnd = Window(None, "YaMusic")
app.MainLoop()
