import praw
from gi.repository import GLib, GObject
from gi.repository import Gtk, Gio, Gdk
from gi.repository import Pango as pango
from threading import Thread

class SubredditView(Gtk.VBox):

    __gtype_name__ = 'SubredditView'
    __gsignals__ = {
        'load_start': (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ()),
        'load_complete': (GObject.SignalFlags.RUN_FIRST, GObject.TYPE_NONE, ())
    }

    def __init__(self, Redd, Sub):
        Gtk.Widget.__init__(self)

        self.Chunk = 30
        self.Reddit = Redd
        self.Subreddit = Sub
        self.Loading = False
        self.PostsLoaded = 0
        self.LastPost = ""
        self.set_style("Style/SubredditView.css")

        self.LastSelectedSort = "Hot"

        self.Grid = Gtk.Grid(column_spacing=0, row_spacing=1)

        self.Act = Gtk.ActionBar()

        self.Spinner = Gtk.Spinner()

        self.Act.pack_start(self.Spinner)

        self.List = Gtk.ListBox()
        self.List.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.Scroll = Gtk.ScrolledWindow(name="post-list")
        self.Scroll.set_border_width(0)
        self.Scroll.set_hexpand(True)
        self.Scroll.set_vexpand(True)
        self.Scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.ALWAYS)
        self.Scroll.connect("edge-reached", self.list_edge)
        self.Scroll.add(self.List)

        self.Grid.attach(self.Scroll, 0, 0, 1, 1)
        self.Grid.attach(self.Act, 0, 1, 1, 1)

        self.add(self.Grid)

    def set_style(self, Sheet):
        cssProvider = Gtk.CssProvider()
        cssProvider.load_from_path(Sheet)
        screen = Gdk.Screen.get_default()
        styleContext = Gtk.StyleContext()
        styleContext.add_provider_for_screen(screen, cssProvider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def get_posts(self):
        List_Chunk = []
        Sub = self.Reddit.get_subreddit(self.Subreddit)

        '''
        Sub.get_new(limit=self.Chunk)
        Sub.get_rising(limit=self.Chunk)
        Sub.get_controversial(limit=self.Chunk)
        Sub.get_top(limit=self.Chunk)
        Sub.get_hot(limit=self.Chunk)

        Sub.get_new(limit=self.Chunk, params={"after" : self.LastPost})
        Sub.get_rising(limit=self.Chunk, params={"after" : self.LastPost})
        Sub.get_controversial(limit=self.Chunk, params={"after" : self.LastPost})
        Sub.get_top(limit=self.Chunk, params={"after" : self.LastPost})
        Sub.get_hot(limit=self.Chunk, params={"after" : self.LastPost})
        '''

        ''' Loading Append '''
        if self.PostsLoaded > 0:
            List_Chunk = Sub.get_hot(limit=self.Chunk, params={"after" : self.LastPost})
        else:
            List_Chunk = Sub.get_hot(limit=self.Chunk)

        return List_Chunk

    def build_interface(self):
        self.Loading = True

        for Post in self.get_posts():
            row = Gtk.ListBoxRow(name="post")
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            row.add(hbox)
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            hbox.pack_start(vbox, True, True, 0)

            Title = Gtk.Label(name="post-title", label=Post.title, xalign=0)
            Title.set_line_wrap(False)
            Title.set_single_line_mode(True)
            Title.set_ellipsize(pango.EllipsizeMode.END)

            Text = Gtk.Label(name="post-content", label=Post.selftext, xalign=0)
            Text.set_line_wrap(False)
            Text.set_single_line_mode(True)
            Text.set_ellipsize(pango.EllipsizeMode.END)

            vbox.pack_start(Title, True, True, 0)
            vbox.pack_start(Text, True, True, 0)

            self.LastPost = Post.fullname
            self.PostsLoaded += 1

            GLib.idle_add(self.load_progress, row)

        self.Loading = False
        GLib.idle_add(self.load_finish)

    def do_load(self):
        if self.PostsLoaded == 0:
            self.emit("load_start")
            self.Spinner.start()
            Thread(target=self.build_interface).start()

    def do_refresh(self):
        for item in self.List.get_children():
            self.List.remove(item)

        self.PostsLoaded = 0
        Thread(target=self.build_interface).start()

    def list_edge(self, Win, Pos):
        if Pos is Gtk.PositionType.BOTTOM:
            if not self.Loading:
                Thread(target=self.build_interface).start()

    def load_progress(self, Row):
        self.List.add(Row)

    def load_finish(self):
        self.show_all()
        self.emit("load_complete")
        self.Spinner.stop()
