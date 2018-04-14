from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Components.config import config
from Tools.Directories import fileExists, pathExists
from ServiceReference import ServiceReference
from enigma import ePicLoad
from os import system
from random import randint



class StandbildView(Screen):
	def __init__(self, session, prvScreen):
		self.skin = prvScreen
		Screen.__init__(self, session)
		self.session = session
		self.whatPic = "/tmp/standbild.jpg"
		self.EXscale = (AVSwitch().getFramebufferScale())
		self.EXpicload = ePicLoad()
		self["Picture"] = Pixmap()
		self["actions"] = ActionMap(["WizardActions"],{"ok": self.SavePic,"back": self.close, }, -1)
		self.EXpicload.PictureData.get().append(self.DecodeAction)
		self.onLayoutFinish.append(self.Show_Picture)

	def Show_Picture(self):
		if fileExists(self.whatPic):
			self.EXpicload.setPara([self["Picture"].instance.size().width(), self["Picture"].instance.size().height(), self.EXscale[0], self.EXscale[1], 0, 1, "#00080808"])
			self.EXpicload.startDecode(self.whatPic)

	def DecodeAction(self, pictureInfo=""):
		if fileExists(self.whatPic):
			ptr = self.EXpicload.getData()
			self["Picture"].instance.setPixmap(ptr)

	def SavePic(self):
		if fileExists(self.whatPic):
			srvName = ServiceReference(self.session.nav.getCurrentlyPlayingServiceReference()).getServiceName()
			srvName = srvName.replace('\xc2\x86', '').replace('\xc2\x87', '')
			srvName = srvName.replace(' ', '_')
			if pathExists(config.usage.timeshift_path.value):
				filename = config.usage.timeshift_path.value + srvName + "-" + str(randint(1000,9999)) + ".jpg"
				command = "cp /tmp/standbild.jpg " + filename
				mtext = "saving picture to...\n" + filename
				self.session.open(MessageBox, text = _(mtext), type = MessageBox.TYPE_INFO)
				system(command)
			else:
				self.session.open(MessageBox, text = _("Location not aviable!"), type = MessageBox.TYPE_ERROR)


