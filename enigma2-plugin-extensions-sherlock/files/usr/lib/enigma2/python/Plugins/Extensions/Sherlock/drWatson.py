#######################################################################
#
#    Doctor Watson for Dreambox-Enigma2
#    Coded by Vali (c)2010
#
#    This plugin is licensed under the Creative Commons 
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License. 
#    To view a copy of this license, 
#    visit http://creativecommons.org/licenses/by-nc-sa/3.0/ 
#    or send a letter to 
#    Creative Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#    Alternatively, this plugin may be distributed and executed on hardware which
#    is licensed by Dream Multimedia GmbH.
#
#    This plugin is NOT free software. It is open source, you are allowed to
#    modify it (if you keep the license), but it may not be commercially 
#    distributed other than under the conditions noted above.
#
#######################################################################



from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import iServiceInformation, ePoint, getDesktop, iFrontendInformation, eTimer
from Plugins.Extensions.BitrateViewer.bitratecalc import eBitrateCalculator



class DoctorWatson(Screen):
	skin = """
		<screen name="DoctorWatson" flags="wfNoBorder" position="50,40" size="150,150" title="Signal-dB">
			<ePixmap alphatest="off" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/bg.png" position="0,0" size="150,150" zPosition="-1"/>
			<widget backgroundColor="#141415" name="caption" font="Regular;18" foregroundColor="#bbbbbf" halign="center" position="0,15" size="150,24" transparent="1"/>
			<eLabel backgroundColor="#141415" font="Regular;18" foregroundColor="#bbbbbf" halign="right" position="0,40" size="60,24" text="->" transparent="1"/>
			<eLabel backgroundColor="#141415" font="Regular;18" foregroundColor="#bbbbbf" halign="right" position="0,65" size="60,24" text="avg" transparent="1"/>
			<eLabel backgroundColor="#141415" font="Regular;18" foregroundColor="#bbbbbf" halign="right" position="0,90" size="60,24" text="min" transparent="1"/>
			<eLabel backgroundColor="#141415" font="Regular;18" foregroundColor="#bbbbbf" halign="right" position="0,115" size="60,24" text="max" transparent="1"/>
			<widget backgroundColor="#141415" name="lcur" position="70,40" foregroundColor="#fec000" size="80,20" font="Regular;18" transparent="1"/>
			<widget backgroundColor="#141415" name="lavg" position="70,65" size="80,20" font="Regular;18" transparent="1"/>
			<widget backgroundColor="#141415" name="lmin" position="70,90" size="80,20" font="Regular;18" transparent="1"/>
			<widget backgroundColor="#141415" name="lmax" position="70,115" size="80,20" font="Regular;18" transparent="1"/>
		</screen>"""
	def __init__(self, session, mode):
		Screen.__init__(self, session)
		self.session = session
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "HelpActions"],
						{
						"ok":self.Exit,
						"cancel": self.Exit,
						"left": self.goLeft,
						"right": self.goRight,
						"up": self.up,
						"down": self.down,
						"displayHelp": self.Exit
						}, -1)
		self["caption"] = Label(_("video bitrate"))
		self["lcur"] = Label(_("0.0"))
		self["lavg"] = Label(_("0.0"))
		self["lmax"] = Label(_("0.0"))
		self["lmin"] = Label(_("0.0"))
		self.dmin = 99999.0
		self.dmax = 0.0
		self.watch4 = mode
		self.ecnt = 5
		self.feinfo = None
		self.haveBorders = True
		self.videoBitrate = None
		self.audioBitrate = None
		self.vbrint = 0
		self.abrint = 0
		self.onLayoutFinish.append(self.sartBitCalc)
		self.DWUpdateTimer = eTimer()
		self.DWUpdateTimer.callback.append(self.updateDWInfo)

	def Exit(self):
		self.close()

	def goLeft(self):
		if self.haveBorders:
			self.instance.move(ePoint(60,90))
		else:
			self.instance.move(ePoint(50,40))

	def goRight(self):
		if self.haveBorders:
			self.instance.move(ePoint((getDesktop(0).size().width()-210),90))
		else:
			self.instance.move(ePoint((getDesktop(0).size().width()-200),40))

	def sartBitCalc(self):
		if self.skinAttributes is not None:
			for (attrib, value) in self.skinAttributes:
				if attrib == "flags":
					self.haveBorders = False
		self.TitleRefresh()
		service = self.session.nav.getCurrentService()
		self.feinfo = (service and service.frontendInfo())
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if not ref:
			return
		vpid = apid = dvbnamespace = -1
		if service:
			serviceInfo = service.info()
			vpid = serviceInfo.getInfo(iServiceInformation.sVideoPID)
			apid = serviceInfo.getInfo(iServiceInformation.sAudioPID)
		if vpid:
			self.videoBitrate = eBitrateCalculator(vpid, ref.toString(), 1000, 1024*1024)
			self.videoBitrate.callback.append(self.getVideoBitrateData)
		if apid:
			self.audioBitrate = eBitrateCalculator(apid, ref.toString(), 1000, 64*1024)
			self.audioBitrate.callback.append(self.getAudioBitrateData)
		self.DWUpdateTimer.start(1000)

	def getVideoBitrateData(self, value, status):
		if status:
			self.vbrint = value
		else:
			self.videoBitrate = None

	def getAudioBitrateData(self, value, status):
		if status:
			self.abrint = value
		else:
			self.audioBitrate = None

	def updateDWInfo(self):
		if self.watch4 == 1:
			x = self.vbrint/1.0
			if x < self.dmin:
				self.dmin = x
			if x > self.dmax:
				self.dmax = x
			self["lcur"].setText("%4.01f" % x)
			self["lmin"].setText("%4.01f" % self.dmin)
			self["lmax"].setText("%4.01f" % self.dmax)
			xavg = float(self["lavg"].getText())
			if not(xavg == 0):
				xavg = (xavg + x)/2.0
			else:
				xavg = x
			self["lavg"].setText("%4.01f" % xavg)
		elif self.watch4 == 2:
			x = self.abrint/1.0
			if x < self.dmin:
				self.dmin = x
			if x > self.dmax:
				self.dmax = x
			self["lcur"].setText("%4.01f" % x)
			self["lmin"].setText("%4.01f" % self.dmin)
			self["lmax"].setText("%4.01f" % self.dmax)
			xavg = float(self["lavg"].getText())
			if not(xavg == 0):
				xavg = (xavg + x)/2.0
			else:
				xavg = x
			self["lavg"].setText("%4.01f" % xavg)
		elif self.watch4 == 3:
			x = 0.0
			if self.ecnt > 4:
				self.ecnt = 0
				try:
					f = open("/tmp/ecm.info", "r")
					flines = f.readlines()
					f.close()
					for cell in flines:
						if ("ecm time:" in cell):
							cellmembers = cell.split()
							for cnt in range(len(cellmembers)):
								if ("time:" in cellmembers[cnt]):
									if cnt<(len(cellmembers)-1):
										x = float(cellmembers[cnt+1])
									else:
										x = 0.0
						elif ("msec" in cell):
							cellmembers = cell.split()
							for cnt in range(len(cellmembers)):
								if ("msec" in cellmembers[cnt]):
									try:
										x = float(cellmembers[cnt-1])/1000.0
									except:
										x = 0.0
				except:
					x = None
				if x is not None:
					if x < self.dmin:
						self.dmin = x
					if x > self.dmax:
						self.dmax = x
					self["lcur"].setText("%2.03f" % x)
					self["lmin"].setText("%2.03f" % self.dmin)
					self["lmax"].setText("%2.03f" % self.dmax)
					xavg = float(self["lavg"].getText())
					if not(xavg == 0):
						xavg = (xavg + x)/2.0
					else:
						xavg = x
					self["lavg"].setText("%2.03f" % xavg)
			else:
				self.ecnt = self.ecnt + 1
		elif self.watch4 == 4:
			if self.feinfo is not None:
				x = (self.feinfo.getFrontendInfo(iFrontendInformation.signalQualitydB) / 100.0)
				if x < self.dmin:
					self.dmin = x
				if x > self.dmax:
					self.dmax = x
				self["lcur"].setText("%3.02f" % x)
				self["lmin"].setText("%3.02f" % self.dmin)
				self["lmax"].setText("%3.02f" % self.dmax)
				xavg = float(self["lavg"].getText())
				if not(xavg == 0):
					xavg = (xavg + x)/2.0
				else:
					xavg = x
				self["lavg"].setText("%3.02f" % xavg)
		elif self.watch4 == 5:
			out_line = open("/proc/loadavg").readline()
			tempX = out_line.split()
			x = float(tempX[0])
			if x is not None:
				if x < self.dmin:
					self.dmin = x
				if x > self.dmax:
					self.dmax = x
				self["lcur"].setText("%3.02f" % x)
				self["lmin"].setText("%3.02f" % self.dmin)
				self["lmax"].setText("%3.02f" % self.dmax)
				xavg = float(self["lavg"].getText())
				if not(xavg == 0):
					xavg = (xavg + x)/2.0
				else:
					xavg = x
				self["lavg"].setText("%3.02f" % xavg)

	def up(self):
		if self.watch4 > 1:
			self.watch4 = self.watch4 - 1
			self["lcur"].setText(_("0.0"))
			self["lavg"].setText(_("0.0"))
			self["lmax"].setText(_("0.0"))
			self["lmin"].setText(_("0.0"))
			self.dmin = 99999.0
			self.dmax = 0.0
			self.ecnt = 5
			self.TitleRefresh()

	def down(self):
		if self.watch4 < 5:
			self.watch4 = self.watch4 +	1
			self["lcur"].setText(_("0.0"))
			self["lavg"].setText(_("0.0"))
			self["lmax"].setText(_("0.0"))
			self["lmin"].setText(_("0.0"))
			self.dmin = 99999.0
			self.dmax = 0.0
			self.ecnt = 5
			self.TitleRefresh()

	def TitleRefresh(self):
		if self.watch4 == 1:
			self["caption"].setText(_("video bitrate"))
		elif self.watch4 == 2:
			self["caption"].setText(_("audio bitrate"))
		elif self.watch4 == 3:
			self["caption"].setText(_("ecm time"))
		elif self.watch4 == 4:
			self["caption"].setText(_("signal dB"))
		elif self.watch4 == 5:
			self["caption"].setText(_("system load"))

