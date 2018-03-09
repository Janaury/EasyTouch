#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import socket
import thread
import threading
import time
import pickle
from common import *


def info(info):
    print '\n######backend: ' + info + '######'

class Session(object):
    def __init__(self, sk, parent):
        self.sk = sk
        self.parent = parent
        ####################################
        self.send_nickname()
        ####################################

    def send_nickname(self):
        nickname = setting['nickname']
        name_package = pickle.dumps(('nickname', nickname))
        self.sk.sendall(name_package)

    def start(self):
        self.send_handler = thread.start_new_thread(self.recv_handle, empty_tuple)

    def send_msg(self, msg):
        msg_package = pickle.dumps(('msg', msg))
        self.sk.sendall(msg_package)

        info('message sended')
        
    def recv_handle(self):
        while True:
            try:
                #################################
                package = self.sk.recv(1024)
                #################################
            except:
                info('connection terminated')

#####################################################################################
                try :
                    result = trans.get(bckend_recv, block= False, timeout = 500)
                except:
                    result = ''
                if result != 'disconnect':
                    trans.send(bckend_center, (bckend_recv, error_disconnected))
                return
#####################################################################################


            if package == u'':
                info('opposite connection terminated')
                try:
                    result = trans.get(bckend_recv, block=False, timeout = 500)
                except:
                    result = ''

                info(result)

                if result != 'disconnect':
                    trans.send(bckend_center, (bckend_recv, error_disconnected))
                return
#####################################################################################
            data = pickle.loads(package)
            if data[0] != 'file':
                trans.send(frntend, data)
            else:
                if data[1] == 'receiving':
                    file_handle.write(data[3])
                elif data[1] == 'start':
                    file_handle = open('./newfile','a+')
                else:
                    file_handle.write(data[3])
                    file_handle.close()
                    trans.send(frntend, (signal_info, u'接收完成'))
#####################################################################################

    def close(self):
        try:
            trans.send(bckend_recv, 'disconnect')
            self.sk.shutdown(socket.SHUT_RDWR)
            self.sk.close()
            info('session closed')
        except:
            trans.get(bckend_recv)
            raise



class Server(object):
    def __init__(self, parent):
        self.accept = True
        self.parent = parent
        
    def listen(self):
        self.address = ('0.0.0.0' ,setting['port'])

        self.listen_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sk.bind(self.address)
        self.listen_sk.listen(5)
        while True:
            try:
                session_sk, address = self.listen_sk.accept()
            except:
                info('listen_stop')

                #########################################
                try:
                    result = trans.get(bckend_listen, timeout=500)
                except:
                    result = ''

                if result != 'stop':
                    trans.send(bckend_center, (bckend_listen, error_stop))

                return
                #########################################

            if self.parent.getConnectState() == True or self.accept == False:
                session_sk.shutdown(socket.SHUT_RDWR)
                session_sk.close()
                continue

            self.parent.setConnectState(True)

            self.session = Session(session_sk, self)

            thread.start_new_thread(self.session.start, empty_tuple)
    
    def closeSession(self):
        self.session.close()

    
    def close(self):
        try:
            trans.send(bckend_listen, 'stop')
            self.listen_sk.shutdown(socket.SHUT_RDWR)
            self.listen_sk.close()
        except:
            trans.get(bckend_listen)
            raise
    
    def __del__(self):
        if hasattr(self, 'listen_sk'):
            self.listen_sk.close()

class Client(object):
    def __init__(self, parent):

        self.parent = parent
    
    def connect(self):
        self.address = (setting['ip'], setting['port'])
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.sk.settimeout(2)
        try:
            self.sk.connect(self.address)
            self.sk.settimeout(None)
        except:
            self.close()
            raise

        self.parent.setConnectState(True)

        self.session = Session(self.sk, self)
        thread.start_new_thread(self.session.start, empty_tuple)

    def closeSession(self):
        self.session.close()

    def close(self):
        self.sk.shutdown(socket.SHUT_RDWR)
        self.sk.close()

class Backend(object):
    def __init__(self):
        self.connected = False
        self.lock = threading.Lock()
        self.server = Server(self)
        self.client = Client(self)


#########################################################################

    def disconnect(self):
        self.setConnectState(False)
        try:
            self.server.closeSession()
            info('server disconnected')
        except:
            self.client.closeSession()
            info('client disconnected')



    def connect(self):
        self.client.connect()


    def send_msg(self, msg):
        try:
            self.client.session.send_msg(msg)
        except:
            self.server.session.send_msg(msg)

    def set_setting(self, setting):
       s.saveSetting(setting)

    def stop_listen(self):
        self.server.close()
        self.server.accept = False

    def start_listen(self):
        thread.start_new_thread(self.server.listen, empty_tuple)
        self.server.accept = True
    def exit(self):
        try:
            self.server.session.close()
            self.server.close()
            self.client.close()
        except:
            pass
        s.saveSetting()

    def front_event(self, data):
        cmd = data
        if cmd == 'connect':

            info('receive signal connect')

            if self.getConnectState() == False:
                try:
                    self.setConnectState(True)
                    self.connect()
                    trans.send(frntend_data, (signal_ok, ))
                except:
                    self.setConnectState(False)
                    trans.send(frntend_data,(signal_error, 'Fail to connect'))
            else:
                trans.send(frntend_data, (signal_info, 'Already connected'))

        elif cmd == 'disconnect':

            info('receive signal disconnect')

            if self.getConnectState() == True:
                self.disconnect()
                trans.send(frntend_data, (signal_ok, ))
            else:
                trans.send(frntend_data, (signal_warning, 'No connection'))
        elif cmd == 'send':

            info('receive signal send')

            if self.getConnectState() == True:
                try:
                    data = trans.get(bckend_data)
                    self.send_msg(data)
                    trans.send(frntend_data, (signal_ok, ))
                except:
                    trans.send(frntend_data, (signal_error, 'Fail to send'))
            else:
                trans.send(frntend_data,(signal_warning, 'No connection'))

        elif cmd == 'save_setting':

            info('receive signal save_setting')

            try:
                new_setting = trans.get(bckend_data)
                self.set_setting(new_setting)
                trans.send(frntend_data, (signal_ok, ))
            except:
                trans.send(data_tunnel, (signal_error, 'Unknown error'))
        elif cmd == 'start_listen':

            info('receive signal start_listen')
            if self.server.accept == False:
                try:
                    self.start_listen()
                    trans.send(frntend_data, (signal_ok, ))
                except:
                    trans.send(frntend_data,(signal_error, 'Fail to start'))
            else:
                trans.send(frntend_data, (signal_info, 'Alreadly listening'))

            info('server is on')
        elif cmd == 'stop_listen':

            info('receive signal stop_listen')

            if self.server.accept == True:
                try:
                    self.stop_listen()
                    trans.send(frntend_data, (signal_ok, ))
                except:
                    trans.send(frntend_data, (signal_error, 'Unknown error'))
            else:
                trans.send(frntend_data, (signal_info, 'Already stopped'))
            info('server is off')
        elif cmd == 'exit':

            info('receive signal exit')
            self.exit()
            trans.send(frntend_data, (signal_ok, ))
            info('backend exited')
            exit()

        else:
            print 'unknown command'

    def recv_event(self, data):
        if data == error_disconnected:
            try:
                self.disconnect()
            except:
                pass
            trans.send(frntend, (signal_warning, u'连接被断开'))

    def listen_event(self, data):
        if data == error_stop:
            self.server.accept = False
            trans.send(frntend, (signal_warning, u'服务器监听被中断'))



##########################################################################

    def start(self):
        thread.start_new_thread(self.server.listen, empty_tuple)

        info('server is listening')

        while True:
            id, data = trans.get(bckend_center)
            if id == frntend:
                self.front_event(data)
            elif id == bckend_recv:
                self.recv_event(data)
            else:
                self.listen_event(data)
####################################################


    def setConnectState(self, state):
        self.lock.acquire()
        self.connected = state
        self.lock.release()

    def getConnectState(self):
        self.lock.acquire()
        state = self.connected
        self.lock.release()
        return state
                
            

            
            
