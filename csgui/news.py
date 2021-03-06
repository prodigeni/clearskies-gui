import os
import wx
import wx.html

from csgui.common import webload, EVT_WEBLOAD


class NewsPanel(wx.html.HtmlWindow):
    def __init__(self, parent, url):
        html = wx.html.HtmlWindow.__init__(self, parent)
        try:
            if os.path.exists(url):
                self.SetPage(file(url).read())
            else:
                self.SetPage("Loading...")
                self.Bind(EVT_WEBLOAD, self.OnWebLoad)
                webload(self, url)
        except Exception as e:
            self.SetPage("Couldn't get %s:\n%s" % (url, str(e)))

    def OnWebLoad(self, evt):
        self.SetPage(evt.GetValue())
