# -*- coding: utf-8 -*-
#
#    Sherlock for Dreambox-Enigma2
#    Version: 7.0
#    Coded by Vali (c)2009-2011
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



from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.PluginBrowser import PluginBrowser
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import config, ConfigSubsection, getConfigListEntry, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Sensors import sensors
from GlobalActions import globalActionMap
from keymapparser import readKeymap, removeKeymap
from enigma import iServiceInformation, getDesktop, eTimer
from os import listdir, system, popen
from standbild import StandbildView
from drWatson import DoctorWatson
from Components.Sources.StaticText import StaticText
from Plugins.Extensions.BitrateViewer.bitratecalc import eBitrateCalculator



back_session = None
config.plugins.Sherlock  = ConfigSubsection()
config.plugins.Sherlock.Mode = ConfigSelection(default="sherlock", choices = [
				("sherlock", _("Sherlock")),
				("drwatson", _("Dr. Watson")),
				("screenshottv", _("TV screenshot")),
				("screenshotosd", _("OSD screenshot")),
				("pluginbrowser", _("PluginBrowser")),
				("showactivescr", _("Show active screens")),
				("help", _("Standard DMM help"))
				])
config.plugins.Sherlock.drWatson = ConfigSelection(default="1", choices = [
				("1", _("Videobitrate")),
				("2", _("Audiobitrate")),
				("3", _("ECM time")),
				("4", _("Signal in dB")),
				("5", _("System loads"))
				])



def autostart(reason, **kwargs):
	if config.plugins.Sherlock.Mode.value == "help":
		return
	help_keymap = "/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/sherlock_keymap.xml"
	if "session" in kwargs:
		global back_session
		back_session = kwargs["session"]
	if reason == 0:
		removeKeymap(help_keymap)
		global globalActionMap
		if 'showSherlock' in globalActionMap.actions:
			del globalActionMap.actions['showSherlock']
		try:
			readKeymap(help_keymap)
		except:
			raise "SHERLOCK - LOAD KEYMAP ERROR !!!"
		globalActionMap.actions['showSherlock'] = autoShow
	elif reason == 1:
		removeKeymap(help_keymap)
		global globalActionMap
		if 'showSherlock' in globalActionMap.actions:
			del globalActionMap.actions['showSherlock']



def autoShow():
	session = back_session
	if session is not None:
		shMode = config.plugins.Sherlock.Mode.value
		if shMode == "sherlock":
			session.open(SherlockII)
		elif (shMode[0]+shMode[1]+shMode[2]) == "scr":
			nowService = session.nav.getCurrentlyPlayingServiceReference()
			session.nav.stopService()
			if shMode == "screenshotosd":
				system("grab -j100 /tmp/standbild.jpg")
			else:
				system("grab -v -j100 /tmp/standbild.jpg")
			w = getDesktop(0).size().width()
			h = getDesktop(0).size().height()
			PreviewString='<screen backgroundColor="#00080808" flags="wfNoBorder" position="0,0" size="'+str(w)+','+str(h)+'" title="Preview">\n'
			PreviewString=PreviewString+' <widget name="Picture" position="0,0" size="'+str(w)+','+str(h)+'" zPosition="5" alphatest="on" />\n'
			PreviewString=PreviewString+' <eLabel font="Regular;18" backgroundColor="#00640808" halign="center" valign="center" position="50,80" size="300,25" text="Please wait....." zPosition="1"/>\n'
			PreviewString=PreviewString+' <eLabel font="Regular;18" backgroundColor="#00080808" halign="center" valign="center" position="50,50" size="300,25" text="OK=Save        Exit=Play TV" zPosition="9"/>\n'
			PreviewString=PreviewString+'</screen>'
			session.open(StandbildView, PreviewString)
			session.nav.playService(nowService)
		elif shMode == "drwatson":
			session.open(DoctorWatson, int(config.plugins.Sherlock.drWatson.value))
		elif shMode == "pluginbrowser":
			session.open(PluginBrowser)
		elif shMode == "showactivescr":
			showDlgStack()
		else:
			session.open(MessageBox, text = _("You have change the Sherlock settings,\nbut not restarted the GUI."), type = MessageBox.TYPE_INFO)



def showDlgStack():
	from Screens.InfoBar import InfoBar
	session = back_session
	DSTK = InfoBar.instance.session.dialog_stack
	if session is not None:
		rettext = "Active Screens:\n"
		for onescr in DSTK:
			rettext = rettext + str(onescr) + "\n"
		session.open(MessageBox, text = rettext, type = MessageBox.TYPE_INFO)



def setup(session, **kwargs):
	session.open(ConfigSherlock)



def main(session, **kwargs):
	session.open(SherlockII)



def Plugins(**kwargs):
 	return [PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = autostart),
			PluginDescriptor(name="Sherlock-Setup", description=_("Configuration tool for Sherlock"), where = PluginDescriptor.WHERE_PLUGINMENU, icon="sherlock.png", fnc=setup),
			PluginDescriptor(name="Sherlock", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]



class ConfigSherlock(ConfigListScreen, Screen):
	skin = """
		<screen name="ConfigSherlock" position="center,center" size="600,340" title="Sherlock settings...">
			<eLabel font="Regular;20" foregroundColor="#00ff4A3C" halign="center" position="20,308" size="120,26" text="Cancel"/>
			<eLabel font="Regular;20" foregroundColor="#0056C856" halign="center" position="165,308" size="120,26" text="Save"/>
			<eLabel font="Regular;20" foregroundColor="#00ffc000" halign="center" position="300,308" size="140,26" text="res."/>
			<eLabel font="Regular;20" foregroundColor="#00879ce1" halign="center" position="455,308" size="120,26" text="res."/>
			<widget name="config" position="5,5" scrollbarMode="showOnDemand" size="590,300"/>
		</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		list = []
		list.append(getConfigListEntry(_("Swap Help button to:"), config.plugins.Sherlock.Mode))
		list.append(getConfigListEntry(_("Doctor Watson mode:"), config.plugins.Sherlock.drWatson))
		ConfigListScreen.__init__(self, list)
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"], 
									{
									"red": self.exit, 
									"green": self.save, 
									"yellow": self.exit,
									"blue": self.exit,
									"cancel": self.exit
									}, -1)

	def save(self):
		for x in self["config"].list:
			x[1].save()
		self.close()

	def exit(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close()



# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



class SherlockII(Screen):
	sz_w = getDesktop(0).size().width()
	if sz_w == 1024:
		skin = """
		<screen backgroundColor="#FF000000" flags="wfNoBorder" position="0,0" size="1024,576" title="Sherlock">
			<widget backgroundColor="#FF000000" position="0,0" render="Pig" size="700,400" source="session.VideoPicture" zPosition="-2"/>
			<eLabel backgroundColor="#141415" position="700,0" size="330,576" zPosition="-1"/>
			<eLabel backgroundColor="#141415" position="0,400" size="710,176" zPosition="-1"/>
			<widget backgroundColor="#141415" font="Regular;20" foregroundColor="#fcc000" halign="left" noWrap="1" position="50,405" render="Label" size="361,25" source="session.CurrentService" transparent="1" valign="center" zPosition="2">
				<convert type="ServiceName">Name</convert>
			</widget>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#f0f0f0" halign="left" position="510,405" render="Label" size="62,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#f0f0f0" halign="left" position="575,405" render="Label" size="86,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNRdB</convert>
			</widget>
			<widget borderColor="#44444a" borderWidth="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/Sherlock_Progress.png" position="430,435" render="Progress" size="228,8" source="session.FrontendStatus" zPosition="3">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#fcc000" halign="left" position="430,405" render="Label" size="74,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">BER</convert>
			</widget>
			<widget backgroundColor="#141415" font="Regular;16" foregroundColor="#f0f0f0" halign="left" noWrap="1" position="130,435" render="Label" size="277,22" source="session.CurrentService" transparent="1" zPosition="2">
				<convert type="ServiceName">Provider</convert>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_crypt_on.png" position="50,520" render="Pixmap" size="24,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsCrypted</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_txt_on.png" position="162,520" render="Pixmap" size="30,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">HasTelext</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_dolby_on.png" position="111,520" render="Pixmap" size="46,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsMultichannel</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_format_on.png" position="79,520" render="Pixmap" size="27,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsWidescreen</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget backgroundColor="#141415" font="Regular;16" foregroundColor="#f0f0f0" name="daten" position="720,95" size="300,306" transparent="1" zPosition="11"/>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#f0f0f0" halign="left" name="dccamdName" noWrap="1" position="720,40" size="300,25" transparent="1" zPosition="3"/>
			<widget render="Label" source="video_bitrate" backgroundColor="#141415" font="Regular;17" foregroundColor="#f0f0f0" halign="left" position="430,460" size="230,20" transparent="1" zPosition="3"/>
			<widget render="Label" source="audio_bitrate" backgroundColor="#141415" font="Regular;17" foregroundColor="#f0f0f0" halign="left" position="430,482" size="230,20" transparent="1" zPosition="3"/>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#f0f0f0" halign="left" name="signal_info" position="50,460" size="317,50" transparent="1" zPosition="3"/>
			<widget backgroundColor="#141415" font="Regular;18" foregroundColor="#f0f0f0" halign="left" name="system_info" position="715,405" size="290,147" transparent="1" zPosition="3"/>
			<widget backgroundColor="#141415" font="Regular;16" foregroundColor="#f0f0f0" halign="left" name="dataFileName" noWrap="1" position="720,70" size="300,22" transparent="1" zPosition="3"/>
			<widget backgroundColor="#141415" font="Regular;16" foregroundColor="#f0f0f0" halign="left" name="OrbitalPosition" noWrap="1" position="50,435" size="77,22" transparent="1" zPosition="4"/>
		</screen>"""
	elif sz_w == 1280:
		skin = """
        <screen backgroundColor="#FF000000" flags="wfNoBorder" name="SherlockII" position="0,0" size="1280,720" title="Sherlock">
			<widget backgroundColor="#FF000000" position="0,0" render="Pig" size="950,534" source="session.VideoPicture" zPosition="-2"/>
			<eLabel backgroundColor="#00111112" position="950,0" size="330,720" zPosition="-1"/>
			<eLabel backgroundColor="#00111112" position="0,530" size="950,190" zPosition="-1"/>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#aaaaac" halign="right" position="1140,45" render="Label" size="86,22" source="global.CurrentTime" transparent="1" zPosition="4">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;20" foregroundColor="#00fcc000" halign="left" noWrap="1" position="70,545" render="Label" size="462,26" source="session.CurrentService" transparent="1" valign="top" zPosition="2">
				<convert type="ServiceName">Name</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;16" foregroundColor="#00aaaaac" halign="left" noWrap="1" position="970,45" render="Label" size="135,22" source="global.CurrentTime" transparent="1" zPosition="3">
				<convert type="ClockToText">Format:%a %d. %b %Y</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" position="635,550" render="Label" size="65,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" position="715,550" render="Label" size="82,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNRdB</convert>
			</widget>
			<widget borderColor="grey" borderWidth="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/Sherlock_Progress.png" position="560,580" render="Progress" size="228,8" source="session.FrontendStatus" zPosition="3">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00fcc000" halign="left" position="560,550" render="Label" size="65,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">BER</convert>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;16" foregroundColor="#00f0f0f0" halign="left" noWrap="1" position="180,580" render="Label" size="347,22" source="session.CurrentService" transparent="1" zPosition="2">
				<convert type="ServiceName">Provider</convert>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_crypt_on.png" position="70,660" render="Pixmap" size="24,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsCrypted</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_txt_on.png" position="182,660" render="Pixmap" size="30,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">HasTelext</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_dolby_on.png" position="131,660" render="Pixmap" size="46,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsMultichannel</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_format_on.png" position="99,660" render="Pixmap" size="27,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsWidescreen</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" name="daten" noWrap="1" position="970,180" size="400,386" transparent="1" zPosition="9"/>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#f0f0f0" halign="left" name="system_info" position="900,545" size="350,180" transparent="1" zPosition="9"/>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" name="dccamdName" noWrap="1" position="970,100" size="300,25" transparent="1" zPosition="3"/>
			<widget render="Label" source="video_bitrate" backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" position="560,610" size="230,20" transparent="1" zPosition="3"/>
			<widget render="Label" source="audio_bitrate" backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" position="560,632" size="230,20" transparent="1" zPosition="3"/>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" name="signal_info" position="70,605" size="461,50" transparent="1" zPosition="3"/>
			<widget backgroundColor="#00111112" font="Regular;16" foregroundColor="#00f0f0f0" halign="left" name="dataFileName" noWrap="1" position="970,140" size="300,22" transparent="1" zPosition="3"/>
			<widget backgroundColor="#00111112" font="Regular;18" foregroundColor="#00f0f0f0" halign="left" name="OrbitalPosition" noWrap="1" position="70,580" size="97,22" transparent="1" zPosition="4"/>
		</screen>"""
	else:
		skin = """
		<screen backgroundColor="#121212" flags="wfNoBorder" position="0,0" size="720,576" title="Sherlock">
			<widget backgroundColor="#FF000000" position="0,0" render="Pig" size="475,356" source="session.VideoPicture" zPosition="-2"/>
			<ePixmap alphatest="off" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/Sherlock_BG-fs8.png" position="0,0" size="720,576" zPosition="-1"/>
			<widget backgroundColor="#080808" font="Regular;18" foregroundColor="#f0f0f0" halign="right" position="580,50" render="Label" size="86,22" source="global.CurrentTime" transparent="1" zPosition="4">
				<convert type="ClockToText">Default</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;23" foregroundColor="#fcc000" halign="center" position="440,81" render="Label" size="230,60" source="session.CurrentService" transparent="1" valign="center" zPosition="2">
				<convert type="ServiceName">Name</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;16" foregroundColor="#f0f0f0" halign="left" noWrap="1" position="440,50" render="Label" size="135,22" source="global.CurrentTime" transparent="1" zPosition="3">
				<convert type="ClockToText">Format:%a %d. %b %Y</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;18" foregroundColor="#f0f0f0" halign="left" position="517,226" render="Label" size="65,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;18" foregroundColor="#f0f0f0" halign="left" position="606,226" render="Label" size="90,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">SNRdB</convert>
			</widget>
			<widget borderColor="#555555" borderWidth="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/Sherlock_Progress.png" position="439,254" render="Progress" size="228,8" source="session.FrontendStatus" zPosition="3">
				<convert type="FrontendInfo">SNR</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;18" foregroundColor="#ffc000" halign="left" position="440,226" render="Label" size="74,25" source="session.FrontendStatus" transparent="1" zPosition="2">
				<convert type="FrontendInfo">BER</convert>
			</widget>
			<widget backgroundColor="#080808" font="Regular;16" foregroundColor="#f0f0f0" halign="left" noWrap="1" position="440,143" render="Label" size="230,22" source="session.CurrentService" transparent="1" zPosition="2">
				<convert type="ServiceName">Provider</convert>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_crypt_on.png" position="500,500" render="Pixmap" size="24,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsCrypted</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_txt_on.png" position="605,500" render="Pixmap" size="30,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">HasTelext</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_dolby_on.png" position="555,500" render="Pixmap" size="46,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsMultichannel</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Sherlock/ico_format_on.png" position="525,500" render="Pixmap" size="27,20" source="session.CurrentService" zPosition="3">
				<convert type="ServiceInfo">IsWidescreen</convert>
				<convert type="ConditionalShowHide"/>
			</widget>
			<widget backgroundColor="#080808" font="Regular;14" foregroundColor="#f0f0f0" name="daten" position="54,362" size="380,166" transparent="1" zPosition="9"/>
			<widget backgroundColor="#080808" font="Regular;14" foregroundColor="#f0f0f0" halign="left" name="system_info" position="440,362" size="280,166" transparent="1" zPosition="9"/>
			<widget render="Label" source="video_bitrate" backgroundColor="#080808" font="Regular;17" foregroundColor="#f0f0f0" halign="left" position="440,269" size="280,20" transparent="1" zPosition="3"/>
			<widget render="Label" source="audio_bitrate" backgroundColor="#080808" font="Regular;17" foregroundColor="#f0f0f0" halign="left" position="440,291" size="280,20" transparent="1" zPosition="3"/>
			<widget backgroundColor="#080808" font="Regular;18" foregroundColor="#f0f0f0" halign="left" name="signal_info" position="440,174" size="280,50" transparent="1" zPosition="3"/>
			<widget backgroundColor="#080808" font="Regular;16" foregroundColor="#f0f0f0" halign="left" name="dataFileName" noWrap="1" position="440,329" size="230,22" transparent="1" zPosition="3"/>
			<widget backgroundColor="#080808" font="Regular;16" foregroundColor="#f0f0f0" halign="right" name="OrbitalPosition" noWrap="1" position="580,174" size="86,22" transparent="1" zPosition="4"/>
		</screen>"""
	def __init__(self, session, args = 0):
		self.session = session
		Screen.__init__(self, session)
		self.InfoFiles = []
		self.IFindex = 0
		self.InfoActive = False
		self.videoBitrate = None
		self.audioBitrate = None
		self["daten"] = Label(_(" "))
		self["system_info"] = Label(_(" "))
		self["signal_info"] = Label(_(" "))
		self["dccamdName"] = Label(_(" "))
		self["video_bitrate"] = StaticText()
		self["audio_bitrate"] = StaticText()
		self["dataFileName"] = Label(_(" "))
		self["OrbitalPosition"] = Label(_(" "))
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "HelpActions"],
		{
			"ok": self.ExitSherlock,
			"cancel": self.ExitSherlock,
			"left": self.left,
			"right": self.right,
			"displayHelp": self.ExitSherlock
		}, -1)
		self.SysUpdateTimer = eTimer()
		self.SysUpdateTimer.callback.append(self.updateSysInfo)
		self.onLayoutFinish.append(self.DataReader)

	def ExitSherlock(self):
		self.close()

	def DataReader(self):
		srv_Text = "N/A"
		ca_Text = " "
		ar_fec = ["Auto", "1/2", "2/3", "3/4", "5/6", "7/8", "8/9", "3/5", "4/5", "9/10", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
		ar_pol = ["H", "V", "CL", "CR", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a", "n/a"]
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		orbital_pos = 0
		if info is not None:
			xresol = info.getInfo(iServiceInformation.sVideoWidth)
			yresol = info.getInfo(iServiceInformation.sVideoHeight)
			feinfo = (service and service.frontendInfo())
			if (feinfo is not None) and (xresol>0):
				srv_Text = "Size: " + str(xresol) + "x" + str(yresol) + "\n"
				frontendData = (feinfo and feinfo.getAll(True))
				if (frontendData is not None):
					if (frontendData.get("tuner_type") == "DVB-S"):
						orbital_pos = int(frontendData["orbital_position"])
						if orbital_pos > 1800:
							self["OrbitalPosition"].setText(str((float(3600 - orbital_pos))/10.0) + "W")
						elif orbital_pos > 0:
							self["OrbitalPosition"].setText(str((float(orbital_pos))/10.0) + "E")
					if ((frontendData.get("tuner_type") == "DVB-S") or (frontendData.get("tuner_type") == "DVB-C")):
						frequency = "FQ:" + str(frontendData.get("frequency") / 1000)
						symbolrate = "SR:" + str(frontendData.get("symbol_rate") / 1000)
						if (frontendData.get("tuner_type") == "DVB-S"):
							polarisation_i = frontendData.get("polarization")
						else:
							polarisation = 0
						fec_i = frontendData.get("fec_inner")
						try:
							srv_Text = srv_Text + frequency + "  " + ar_pol[polarisation_i] + "  " + ar_fec[fec_i] + "  " + symbolrate
						except:
							srv_Text = srv_Text + frequency + "    " + symbolrate
					elif (frontendData.get("tuner_type") == "DVB-T"):
						frequency = str(frontendData.get("frequency") / 1000) + " MHz"
						srv_Text = srv_Text + frequency
		self["signal_info"].setText(_(srv_Text))
		self["dccamdName"].setText(self.is_dccamd_running())
		self.searchInfoFiles()
		self.updateSysInfo()
		self.SysUpdateTimer.start(5000)
		ref = self.session.nav.getCurrentlyPlayingServiceReference()
		if not ref:
			return
		vpid = apid = dvbnamespace = -1
		service = self.session.nav.getCurrentService()
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

	def getVideoBitrateData(self,value, status):
		if status:
			self["video_bitrate"].text = "Video: %d kbit/s" % value;
		else:
			self.videoBitrate = None

	def getAudioBitrateData(self,value, status):
		if status:
			self["audio_bitrate"].text = "Audio: %d kbit/s" % value;
		else:
			self.audioBitrate = None

	def is_dccamd_running(self):
		try:
			mylist = open("/etc/clist.list", "r")
		except:
			return " "
		dccamd = "N/A"
		if mylist is not None:
			for current in mylist:
				dccamd = current
			mylist.close()
			return dccamd
		else:
			return "N/A"

	def updateSysInfo(self):
		try:
			out_line = open("/proc/loadavg").readline()
			ret = "load average   " + out_line[:15] + "\n"# + "\n"
			out_lines = []
			out_lines = open("/proc/meminfo").readlines()
			for lidx in range(len(out_lines)-1):
				tstLine = out_lines[lidx].split()
				if "MemFree:" in tstLine:
					ret = ret + out_lines[lidx]
			out_lines = popen("df -h").readlines()
			out_line = out_lines[1]
			if len(out_line.split()) > 4:
				out_line = "FreeFlash: "+out_line.split()[3]+"B   used: "+out_line.split()[4]+"\n"
				ret = ret + out_line
			res = ""
			service = self.session.nav.getCurrentService()
			info = service and service.info()
			if info is not None:
				if info.getInfo(iServiceInformation.sIsCrypted):
					searchIDs =(info.getInfoObject(iServiceInformation.sCAIDs))
					for oneID in searchIDs:
						if res:
							res = res + ", "
						temp_str = hex(oneID).lstrip("0x")
						if (len(temp_str)==4):
							res = res + temp_str.upper()
						else:
							res = res + "0" + temp_str.upper()
					res = "max.Temp " + self.TempMessung() + "\ncaid " + res
				else:
					res = res + "\nmax.Temp " + self.TempMessung()
			ret = ret + res
		except:
			ret = "N/A"
		self["system_info"].setText(_(ret))
		if len(self.InfoFiles) > 0:
			try:
				f = open(self.InfoFiles[self.IFindex], "r")
				data_lines=f.readlines()
				f.close()
				Data_Text=""
				for i in range(0, len(data_lines)):
					Data_Text = Data_Text + data_lines[i]
			except:
				Data_Text="No data-file found."
			self["daten"].setText(_(Data_Text))
			self["dataFileName"].setText(self.InfoFiles[self.IFindex])

	def searchInfoFiles(self):
		files = listdir('/tmp/')
		files.sort()
		for name in files:
			testname = name.lower()
			if testname.endswith(".info"):
				self.InfoFiles.append('/tmp/'+name)

	def left(self):
		self.IFindex = self.IFindex - 1
		if self.IFindex < 0:
			self.IFindex = len(self.InfoFiles)-1
		self.updateSysInfo()

	def right(self):
		self.IFindex = self.IFindex + 1
		if self.IFindex > (len(self.InfoFiles)-1):
			self.IFindex = 0
		self.updateSysInfo()

	def TempMessung(self):
		maxtemp = 0
		sensotN = "?"
		try:
			templist = sensors.getSensorsList(sensors.TYPE_TEMPERATURE)
			tempcount = len(templist)
			for count in range(tempcount):
				id = templist[count]
				tt = sensors.getSensorValue(id)
				if tt > maxtemp:
					maxtemp = tt
					sensotN = sensors.getSensorName(id)
					if sensotN == "undefined":
						sensotN = "sensor-"+str(id)
		except:
			pass
		return str(maxtemp) + "°C / " + sensotN




