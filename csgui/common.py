import os
import sys
import wx
import logging
import threading
import requests


log = logging.getLogger(__name__)


def resource(path):
    """
    Given that X was in our folder in development, where could it be now?

    - PyInstaller one-dir mode: in the same folder as the .exe
    - One-file mode: in a temporary unpacking folder
    - We're still in development: the current folder
    - We're on a mac: a couple of folders up from the binary

    Try all of those, return the first file path that exists
    """
    ideas = [
        os.path.join(os.path.dirname(sys.argv[0]), path),
        os.path.join(getattr(sys, "_MEIPASS", "/"), path),
        os.path.join(os.environ.get("_MEIPASS2", "/"), path),
        path,
    ]
    for n in range(0, 5):
        parts = ([".."] * n + [path])
        ideas.append(os.path.join(*parts))
    for p in ideas:
        if os.path.exists(p):
            log.debug("Found %s at %s" % (path, p))
            return p
    log.warn("Can't find %s" % path)
    log.debug("Tried: %r" % ideas)
    return None


def icon_bundle(fn):
    """
    wx doesn't automatically load all the different sizes from a .ico :(
    """
    icons = wx.IconBundle()
    for sz in [16, 32, 48]:
        try:
            icon = wx.Icon(fn, wx.BITMAP_TYPE_ICO, desiredWidth=sz, desiredHeight=sz)
            icons.AddIcon(icon)
        except Exception:
            pass
    return icons


myEVT_WEBLOAD = wx.NewEventType()
EVT_WEBLOAD = wx.PyEventBinder(myEVT_WEBLOAD, 1)


class WebLoadEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value

    def GetValue(self):
        return self._value


def webload(parent, url, eid=-1):
    t = threading.Thread(target=_webload, args=(parent, url, eid))
    t.start()


def _webload(parent, url, eid=-1):
    try:
        data = requests.get(url).text
    except Exception as e:
        data = "Couldn't get %s:\n%s" % (url, str(e))
    wx.PostEvent(parent, WebLoadEvent(myEVT_WEBLOAD, eid, data))
