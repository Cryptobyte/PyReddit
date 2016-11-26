import praw
from gi.repository import WebKit
from gi.repository import Gtk, Gio, Gdk

class PostView(Gtk.VBox):

    __gtype_name__ = 'PostView'

    def __init__(self, Redd, Post):
        Gtk.Widget.__init__(self)
