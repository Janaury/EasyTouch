#!/usr/bin/env python
#_*_ coding:utf-8 _*_

import socket
import thread
import threading
import time
from common import *


class Session(object):
    def __init__(self, sk, parent):
        self.sk = sk
        self.messager = parent.messager
        self.receive_queue = parent.messager.b2f_buff
        self.send_queue = parent.messager.f2b_buff

    def start(self):
        self.send_handler = thread.start_new_thread(self.recv_handle, empty_tuple)

    def send_handle(self):
        message_byte = self.send_queue.get()
        try:
            message = self.messager.b2r_signal.get(block=False)
            if message == 'exit':
                return
        except:
            pass
        self.sk.sendall(message_byte)

        print '\n######backend: message sended######'
        
    def recv_handle(self):
        while True:
            message_byte = self.sk.recv(1024)

            print type(message_byte)
            if message_byte == u'':
                info('connection terminated')
                self.messager.f2b_signal.put('disconnect')
                self.messager.b2f_signal.get()
                time.sleep(1)
                self.messager.b2f_notice.put(u'连接被断开')
                return
            self.receive_queue.put(message_byte)
            time.sleep(3)

        print '\n######backend: message received ' +message_byte+ ' ######'
    def close(self):
        try:
            self.sk.close()
            print '\n######backend: session closed######'
        except:
            pass



class Server(object):
    def __init__(self, parent):

        self.accept = True
        self.messager = parent.messager
        self.parent = parent
        self.address = ('127.0.0.1',12345)
        
    def listen(self):
        self.address = ('127.0.0.1',self.parent.address[1])
        self.listen_sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sk.bind(self.address)
        self.listen_sk.listen(5)
        while True:
            try:
                session_sk, address = self.listen_sk.accept()
            except:
                info('listen_stop')
                return

            if self.parent.getConnectState() == True or self.accept == False:
                session_sk.close()
                continue

            self.parent.setConnectState(True)

            self.session = Session(session_sk, self)
            thread.start_new_thread(self.session.start, empty_tuple)
    
    def closeSession(self):
        try:
            self.messager.b2r_signal.put('exit', block=False)
            self.session.close()
        except:
            pass
    
    def close(self):
        try:
            self.listen_sk.shutdown(socket.SHUT_RDWR)
            self.listen_sk.close()
        except:
            pass
    
    def __del__(self):
        if hasattr(self, 'listen_sk'):
            self.listen_sk.close()

class Client(object):
    def __init__(self, parent):

        self.parent = parent
        self.messager = parent.messager
    
    def connect(self):
        self.address = self.parent.address
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sk.settimeout(2)
        self.sk.connect(self.address)
        self.sk.settimeout(None)


        self.parent.setConnectState(True)

        self.session = Session(self.sk, self)
        thread.start_new_thread(self.session.start, empty_tuple)

    def closeSession(self):
        try:
            self.messager.b2r_signal.put('exit', block=False)
            self.session.close()
        except:
            pass

    def close(self):
        try:
            self.sk.close()
        except:
            pass

class Backend(object):
    def __init__(self, messager, address = ('127.0.0.1', 12345), file_path = '~/public'):
        self.connected = False
        self.lock = threading.Lock()
        self.messager = messager
        self.file_path = file_path
        self.address = address
        self.server = Server(self)
        self.client = Client(self)
    def start(self):
        thread.start_new_thread(self.server.listen, empty_tuple)

        info('server is listening')

        while True:
            cmd = self.messager.f2b_signal.get()
           
            if cmd == 'connect':
                
                info('receive signal connect')

                if self.getConnectState() == False:
                    try:
                        self.client.connect()
                        self.messager.b2f_signal.put('ok')
                    except:
                        self.messager.b2f_signal.put('fail to connect')
                else:
                    self.messager.b2f_signal.put('already connected')
            elif cmd == 'disconnect':

                info('receive signal disconnect')

                if self.getConnectState() == True:
                    try:
                        self.server.closeSession()
                        info('server disconnected')
                    except:
                        self.client.closeSession()
                        info('client disconnected')

                    self.setConnectState(False)
                    self.messager.b2f_signal.put('ok')
                else:
                    self.messager.b2f_signal.put('no connection')
            elif cmd == 'send':

                info('receive signal send')

                if self.getConnectState() == True:
                    try:
                        try:
                            self.client.session.send_handle()
                        except:
                            self.server.session.send_handle()

                        self.messager.b2f_signal.put('ok')
                    except:
                        self.messager.b2f_signal.put('fail to send')
                else:
                    self.messager.b2f_signal.put('no connection')
            elif cmd == 'read_setting':

                info('receive signal read_setting')

                setting = {
                    'address' : self.address,
                    'file_path': self.file_path
                }
                self.messager.b2f_signal.put(setting)
            elif cmd == 'save_setting':
                
                info('receive signal save_setting')

                new_setting = self.messager.f2b_buff.get()
                self.address = new_setting['address']
                self.file_path = new_setting['file_path']
                self.messager.b2f_signal.put('ok')
            elif cmd == 'start_listen':

                info('receive signal start_listen')
                if self.server.accept == True:
                    self.messager.b2f_signal.put('already listening')
                    continue
                try:
                    self.server.accept = True
                    thread.start_new_thread(self.server.listen, empty_tuple)
                    self.messager.b2f_signal.put('ok')
                except:
                    self.server.accept = False
                    self.messager.b2f_signal.put('fail to start')

                info('server is on')
            elif cmd == 'stop_listen':

                info('receive signal stop_listen')

                if self.server.accept == False:
                    self.messager.b2f_signal.put('server not running')
                    continue
                try:
                    self.server.accept = False
                    self.server.close()
                    self.messager.b2f_signal.put('ok')
                except:
                    self.server.accept = False
                    self.messager.b2f_signal.put('fail to stop')
                info('server is off')
            elif cmd == 'exit':

                info('receive signal exit')
                self.server.close()
                self.client.close()
                self.messager.b2f_signal.put('backend_exited')

                info('backend exited')
                break

            else:
                print 'unknown command'

    def setConnectState(self, state):
        self.lock.acquire()
        self.connected = state
        self.lock.release()

    def getConnectState(self):
        self.lock.acquire()
        state = self.connected
        self.lock.release()
        return state
                
            

            
            