#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import Queue

empty_tuple = ()

def info(info):
    print '\n######backend: ' + info + '######'

class Messager(object):
    def __init__(self):
        self.b2f_buff = Queue.Queue()
        self.f2b_buff = Queue.Queue()
        self.b2f_signal = Queue.Queue()
        self.f2b_signal = Queue.Queue()
        self.b2r_signal =Queue.Queue()
        self.b2l_signal = Queue.Queue()
        self.b2f_notice = Queue.Queue()
