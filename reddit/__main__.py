# __main__.py
#
# Copyright (C) 2016 Cryptobyte
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
import praw
import sys
import urllib3
import OAuth2Util
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import GLib, GObject
from gi.repository import Gtk, Gio, Gdk
from gi.repository import Pango as pango
from threading import Thread

from Widgets.PostView import PostView
from Widgets.SubredditView import SubredditView

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Reddit")

        self.set_title("Reddit")
        self.set_default_size(800, 500)
        self.set_icon_from_file('reddit.png')

        self.connect('destroy', Gtk.main_quit)
        self.connect("delete-event", self.app_quit)

        self.account_ui_refresh()

        global Subs_Loaded
        Subs_Loaded = []

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.set_title("Reddit")
        hb.set_subtitle("The Front Page of the Internet")

        self.set_titlebar(hb)

        main_grid = Gtk.Grid(column_spacing=0, row_spacing=1)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_tab_pos(Gtk.PositionType.LEFT)
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        self.notebook.add_events(Gdk.EventMask.SCROLL_MASK | Gdk.EventMask.SMOOTH_SCROLL_MASK)
        self.notebook.connect("switch-page", self.click_Subreddit)
        self.notebook.connect('scroll-event', self.notebook_scroll)

        main_grid.attach(self.notebook, 0, 0, 1, 1)

        self.add(main_grid)
        self.show_all()
        self.build_Subreddits()

    def notebook_scroll(self, widget, event):
        if event.get_scroll_deltas()[2] < 0:
            self.notebook.prev_page()
        else:
            self.notebook.next_page()

    def get_Subreddits(self):
        Subreddits = []

        if r.user == None:
            for Sub in r.get_popular_subreddits():
                Sub_Name = Sub.url.split('/')[2]
                Subreddits.append(Sub_Name)
        else:
            for Sub in r.get_my_subreddits():
                Sub_Name = Sub.url.split('/')[2]
                Subreddits.append(Sub_Name)

        return Subreddits

    def click_Subreddit(self, Book, Page, pageNum):
        TabChild = Book.get_nth_page(pageNum)
        TabLabel = Book.get_tab_label(TabChild)
        TabText  = TabLabel.get_text()

        if TabText in Subs_Loaded:
            Page.do_load()

        else:
            Subs_Loaded.append(TabText)

    def build_Subreddits(self):
        Subreddits = self.get_Subreddits()

        while self.notebook.get_n_pages():
            self.notebook.remove_page(0)

        self.notebook.queue_draw_area(0, 0, -1, -1)

        Subs_Loaded[:] = []

        for Sub in Subreddits:
            self.notebook.append_page(SubredditView(r, Sub), Gtk.Label(label=Sub))

        self.notebook.show_all()

    def account_ui_refresh(self):
        o.refresh(force=True)

    def app_about(self, widget):
        dialog = Gtk.AboutDialog()
        dialog.set_program_name("Reddit")
        dialog.set_version("0.0.1")
        dialog.set_authors(["Cryptobyte"])
        dialog.set_artists(["Roundicons"])
        dialog.set_license("")
        dialog.set_comments(
            "This painful mess was my first ever PyGTK application. " +
            "It's probably not on par with any coding standards but it seems to work. " +
            "If you find something that doesn't work let me know via the Github page " +
            "and i will make some messy spaghetti code fix unless my PyGTK skills have " +
            "significantly improved.")

        dialog.set_website_label("Github")
        dialog.set_website("https://github.com/Cryptobyte")
        dialog.connect('response', lambda dialog, data: dialog.destroy())
        dialog.show_all()

    def app_quit(event, self, widget):
        return False

r = praw.Reddit('Reddit for Gnome by /u/H4x0')
o = OAuth2Util.OAuth2Util(r, configfile="Config.ini")
win = MainWindow()
win.show_all()
Gtk.main()
