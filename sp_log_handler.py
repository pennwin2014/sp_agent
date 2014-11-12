# coding=utf-8
__author__ = 'Penn'

import datetime
import os

FRAME_LENGTH = 16

class sp_log_handler:
    def sp_classify_log(self, path, transdtl, fid):
        #path = u"transdtl_logs"
        new_path = path
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
        fileHandler = open(
            new_path + "\\{0}.log".format(datetime.date.today()), 'a')
        fileHandler.write("====================\ntime={0:02d}:{1:02d}:{2:02d}, fid={3}\n=================={4}\n".format(
            datetime.datetime.now().hour, datetime.datetime.now().minute,
            datetime.datetime.now().second, fid, transdtl))
        fileHandler.close()


    def sp_brief_log(self, m_str, issend):
        path = u"logs"
        title = u"{0}".format(datetime.date.today())
        new_path = os.path.join(path, title)
        if issend:
            sub_title = u"send_brief_logs"
        else:
            sub_title = u"recv_brief_logs"
        new_path = os.path.join(new_path, sub_title)
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
        fileHandler = open(
            new_path + "\\{0:02d}{1:02d}{2:02d}.log".format(datetime.datetime.now().hour, datetime.datetime.now().minute,
                                                            datetime.datetime.now().second), 'a')
        fileHandler.write("数据总字节数={0}\n".format(len(m_str)))
        for i in range(0, len(m_str), 1):
            fileHandler.write("[{0:02x}]".format(ord(m_str[i])))
        fileHandler.close()


    def sp_detail_log(self, m_str, issend):
        path = u"logs"
        title = u"{0}".format(datetime.date.today())
        new_path = os.path.join(path, title)
        if issend:
            sub_title = u"send_detail_logs"
        else:
            sub_title = u"recv_detail_logs"
        new_path = os.path.join(new_path, sub_title)
        if not os.path.isdir(new_path):
            os.makedirs(new_path)
        fileHandler = open(
            new_path + "\\{0:02d}{1:02d}{2:02d}.log".format(datetime.datetime.now().hour, datetime.datetime.now().minute,
                                                            datetime.datetime.now().second), 'a')
        fileHandler.write("数据总字节数={0}，分为{1}帧\n".format(len(m_str), len(m_str) / FRAME_LENGTH))
        for i in range(0, len(m_str), 1):
            if i % 4 == 0:
                fileHandler.write("\n")
            if i % FRAME_LENGTH == 0:
                fileHandler.write("第{0}帧==================\n".format(i / FRAME_LENGTH + 1))
            fileHandler.write("[{0:02x}]".format(ord(m_str[i])))
        fileHandler.close()


    def print_hex(self, m_str):
        for i in range(0, len(m_str), 1):
            print "{0:02X},".format(ord(m_str[i])),