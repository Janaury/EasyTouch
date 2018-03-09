#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import Queue
import wx
import json

empty_tuple = ()



#############################
# new communication class
#############################

class Transport(object):

    def __init__(self):
        self.sheet = dict()
        for id in (bckend_recv, bckend_center, bckend_listen, frntend, frntend_data, bckend_data):
            self.enroll(id)
    def enroll(self, id):
        if not self.sheet.has_key(id):
            self.sheet[id] = Queue.Queue()
        else:
            raise RuntimeError(id + ' has been enrolled')

    def send(self, id, data, block = True, timeout = None):
        self.sheet[id].put(data, block = block, timeout = timeout)

    def get(self, id, block = True, timeout = None):
        return self.sheet[id].get(block = block, timeout = timeout)

    def cancel(self, id):
        if self.sheet.has_key(id):
            self.sheet.pop(id)
        else:
            raise  RuntimeError(id + ' doesn\'t exist')

class Setting(object):
    def __init__(self):
        self.path = './setting.json'
        try:
            setting_file = open(self.path,'r')
            self.setting = json.load(setting_file, encoding = 'utf-8')
            setting_file.close()
        except:
            self.setting = {
                'nickname' : u'王小明',
                'ip' : '127.0.0.1',
                'port' : 12345,
                'file_path' : '~/public'
            }

    def changeSetting(self, setting):
        self.setting = setting

    def saveSetting(self):
        setting_file = open(self.path, 'w')
        json.dump(self.setting, setting_file)

s = Setting()
setting = s.setting


##################
#   thread id
##################
bckend_center = 1
bckend_recv = 2
bckend_listen = 3
bckend_data = 4

frntend_data = 5
frntend = 6

#############################
# temporary data tunnel id
#############################
data_tunnel = 10


############################
#
############################
signal_ok = 20
signal_warning = wx.ICON_EXCLAMATION
signal_error = wx.ICON_ERROR
signal_info = wx.ICON_INFORMATION

##################
#   signal
##################
error_disconnected = 51
error_stop = 52
on_connect = 1
on_disconnect = 2
on_send = 3
on_read_setting = 4
on_set_setting = 5
on_stop_listen = 6
on_start_listen = 7


trans = Transport()









