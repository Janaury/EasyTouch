#!/usr/bin/env python
#_*_ coding:utf-8 _*_

#####################
#       EasyTouch
#####################
#this program works on python2

from backend import *
from frontend import *
from common import *
import thread


backend = Backend()
thread.start_new_thread(backend.start, empty_tuple)
frontend = Frontend()
frontend.start()
print 'exit'

#messager.f2b_signal.put('exit')





