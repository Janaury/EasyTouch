#!/usr/bin/env python
#_*_ coding:utf-8 _*_

#####################
#       CoLANct
#####################
#this program works on python2

from backend import *
from frontend import *
from common import *
import thread

messager = Messager()

backend = Backend(messager)
thread.start_new_thread(backend.start, empty_tuple)
frontend = Frontend(messager)
frontend.start()
print 'exit'

#messager.f2b_signal.put('exit')





