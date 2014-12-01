# coding=utf-8
__author__ = 'Penn'

import sp_log_handler
import sp_datalist
import struct

FRAME_LENGTH = 16
DATA_HEADER_CPY_STR = "<3sBH2sI"
DATA_HEADER_LEN = 12
TRANSDTL_CPY_STR = "<IIH3sIB6s6sIHI3s6s6s4sB2s2s"  # "IIH3sIB6s6sIBI3s6s6s4sB2s2s144s"
AUTH_CPY_STR = "<4s3s7s4s4s"
FLAG_SEND = True
FLAG_RECV = False
gloabal_log_handler = sp_log_handler.sp_log_handler()
global_cnt = 1
class sp_hd_handler():
    def __init__(self):
        list_handler = sp_datalist.sp_datalist_handler()
        recieved_buffer = ""
        blacklist_verno = ""
        feerate_verno = 1
        timepara_verno = 1
        syspara_verno = 1

    def prepare_verno(self):
        global global_cnt
        if global_cnt == 1:
            global_cnt += 1
            import time
            import binascii
            svrtime = time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))
            #黑名单版本号
            self.blacklist_verno = binascii.unhexlify(svrtime)
            #接收到的流水号
            self.recv_transdtl_no = 1
        #系统参数版本号
        self.syspara_verno = 2
        #费率版本号
        self.feerate_verno = 2
        #时间段参数版本号
        self.timepara_verno = 2


    def handle_auth(self, auth_data, fid):
        print u"收到一次签到"
        termno, soft_verno, cur_datetime, feerate_verno, syspara_verno = struct.unpack(AUTH_CPY_STR, auth_data)
        log_str = ""
        tmp_str = u"\ntermno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(termno[0]), ord(termno[1]), ord(termno[2]),
                                                                    ord(termno[3]))
        log_str += tmp_str
        tmp_str = u"\nsoft_verno={0:02x}{1:02x}{2:02x}\n".format(ord(soft_verno[0]), ord(soft_verno[1]),
                                                                 ord(soft_verno[2]))
        log_str += tmp_str
        tmp_str = u"\ncur_datetime={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}\n".format(ord(cur_datetime[0]), ord(cur_datetime[1]),
                                ord(cur_datetime[2]), ord(cur_datetime[3]), ord(cur_datetime[4]), ord(cur_datetime[5]), ord(cur_datetime[6]))
        log_str += tmp_str
        tmp_str = u"\nfeerate_verno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(feerate_verno[0]), ord(feerate_verno[1]),
                                                                           ord(feerate_verno[2]), ord(feerate_verno[3]))
        log_str += tmp_str
        tmp_str = u"\nsyspara_verno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(syspara_verno[0]), ord(syspara_verno[1]),
                                                                           ord(syspara_verno[2]), ord(syspara_verno[3]))
        log_str += tmp_str
        path = u"auth_logs"
        gloabal_log_handler.sp_classify_log(path, log_str, fid)

    def handle_transdtl(self, transdtl, fid):
        # print u"transdtl_len={0}".format(len(transdtl))
        termseqno, cardno, lastcnt, lastlimamt, lastamount, lasttransflag, lasttermno, lastdatetime, cardbefbal, cardbefcnt, amount, \
        extraamount, transdatetime, psamno, tac, transflag, reserve, crc = struct.unpack(TRANSDTL_CPY_STR, transdtl)
        log_str = ""
        tmp_str = u"\ntermseqno={0}\ncardno={1}\nlastcnt={2}\n".format(termseqno, cardno, lastcnt)
        log_str += tmp_str
        tmp_str = u"lastlimamt=[{0:02X}][{1:02x}][{2:02x}]\n".format(ord(lastlimamt[0]), ord(lastlimamt[1]),
                                                                     ord(lastlimamt[2]))
        log_str += tmp_str
        tmp_str = u"lastamt={0}\n".format(lastamount)
        log_str += tmp_str
        tmp_str = u"lasttransflag={0:02x}\nlasttermno={1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}\n".format(
            lasttransflag,
            ord(lasttermno[0]), ord(lasttermno[1]), ord(lasttermno[2]), ord(lasttermno[3]), ord(lasttermno[4]),
            ord(lasttermno[5]))
        log_str += tmp_str
        tmp_str = u"lastdatetime={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}\n".format(ord(lastdatetime[0]),
                                                                                      ord(lastdatetime[1]),
                                                                                      ord(lastdatetime[2]),
                                                                                      ord(lastdatetime[3]),
                                                                                      ord(lastdatetime[4]),
                                                                                      ord(lastdatetime[5]))
        log_str += tmp_str
        tmp_str = u"cardbefbal={0}\ncardbefcnt={1}\namount={2}\n".format(cardbefbal, cardbefcnt, amount)
        log_str += tmp_str
        tmp_str = u"extraamount=[{0:02x}][{1:02x}][{2:02x}]\n".format(ord(extraamount[0]), ord(extraamount[1]),
                                                                      ord(extraamount[2]))
        log_str += tmp_str
        tmp_str = u"transdatetime={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}\n".format(ord(transdatetime[0]),
                                                                                       ord(transdatetime[1]),
                                                                                       ord(transdatetime[2]),
                                                                                       ord(transdatetime[3]),
                                                                                       ord(transdatetime[4]),
                                                                                       ord(transdatetime[5]))
        log_str += tmp_str
        tmp_str = u"psamno={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}\n".format(ord(psamno[0]), ord(psamno[1]),
                                                                                ord(psamno[2]),
                                                                                ord(psamno[3]), ord(psamno[4]),
                                                                                ord(psamno[5]))
        log_str += tmp_str
        tmp_str = u"tac={0:02x}{1:02x}{2:02x}{3:02x}\ntransflag={4:02x}\nreserve={5:02x}{6:02x}\ncrc={7:02x}{8:02x}\n".format(
            ord(tac[0]), ord(tac[1]), ord(tac[2]), ord(tac[3]), transflag, ord(reserve[0]), ord(reserve[1]),
            ord(crc[0]), ord(crc[1]))
        log_str += tmp_str
        path = u"transdtl_logs"
        gloabal_log_handler.sp_classify_log(path, log_str, fid)
        tmp_str = u"amount={4},tac={0:02X}{1:02X}{2:02X}{3:02X}".format(ord(tac[0]), ord(tac[1]), ord(tac[2]),
                                                                        ord(tac[3]), amount)
        # print tmp_str
        self.print_words(u"收到一笔流水，transflag={0:02X}".format(transflag))
        return termseqno

    @staticmethod
    def print_words(words):
        import time
        print u"{0}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))),
        print words

    def print_can_data(self, data):
        self.print_words("data=")
        for i in range(0, len(data)):
            print "{0:02x}".format(ord(data[i])),
    def prepare_data_by_cmd(self, cmd_code, recv_data,fid):
        data = ""
        self.prepare_verno()
        print "cmd={0:02x}".format(cmd_code)
        if cmd_code == 0x00:
            self.print_words(u"收到链路检测")
            data = "\x00\x01\x03"
        elif cmd_code == 0xD2:
            termseqno = self.handle_transdtl(recv_data, fid)
            self.recv_transdtl_no = termseqno
            retcode = 0
            data = struct.pack("<BIs", retcode, termseqno, '1')
        elif cmd_code == 0xD3:  # 签到
            self.handle_auth(recv_data, fid)
            import time
            svrtime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            import binascii
            #是否需要更新时钟
            send_data = "\x01"
            #系统时钟
            send_data += binascii.unhexlify(svrtime)
            #费率版本号
            send_data += struct.pack(">I", self.feerate_verno)
            #主参数版本
            send_data += struct.pack(">I", self.syspara_verno)
            #时间段参数版本
            send_data += struct.pack(">I", self.timepara_verno)
            data = send_data
        elif cmd_code == 0xDA:
            self.print_words(u"收到获取黑名单请求")
            self.print_can_data(recv_data)
            max_page_cnt = 10
            index = struct.unpack("<H", recv_data)
            index = index[0]
            print u"收到index={0}".format(index)
            index += 1
            end_flag = 0
            if index> max_page_cnt:
                end_flag = 1
            #当前序号
            data += struct.pack(">H", index)
            #是否结束
            data += struct.pack("B", end_flag)
            #本次的字节数
            data += struct.pack(">H", 128)
            #准备黑名单位图 128*10
            test_data = []
            for i in range(0, 128, 1):
                test_data.append(chr(0xFF))
            blacklist_bitmap = "".join(test_data)
            data += blacklist_bitmap
        elif cmd_code == 0xD5:
            self.print_words(u"收到心跳")
            #解析接收到的心跳数据
            pos_time, pos_send_transno, pos_transno =struct.unpack("!6sII", recv_data)
            #黑名单版本号
            send_data = self.blacklist_verno
            #主系统参数版本号
            send_data += struct.pack(">I", self.syspara_verno)
            #费率表版本号
            send_data += struct.pack(">I", self.feerate_verno)
            #时间段参数版本号
            send_data += struct.pack(">I", self.timepara_verno)
            #已接收到的流水号
            send_data += struct.pack(">I", self.recv_transdtl_no)
            #当前流水号
            send_data += struct.pack(">I", pos_transno)
            #pos机时间
            send_data += pos_time
            data = send_data
        elif cmd_code == 0xDC:
            self.print_words(u"收到下载费率表请求")
            test_data = []
            for i in range(0, 256, 1):
                test_data.append(chr(120))
            feerate_table = "".join(test_data)
            data = feerate_table
            #允许使用卡类别位图
            test_data = []
            for i in range(0, 32, 1):
                test_data.append(chr(0xFF))
            feetype_bitmap = "".join(test_data)
            data += feetype_bitmap
        elif cmd_code == 0x06:
            self.print_words(u"收到下载主参数")
            #主参数版本号
            pos_syspara_verno = struct.unpack(">I", recv_data)
            pos_syspara_verno = pos_syspara_verno[0]
            upd_flag = 0
            if pos_syspara_verno != self.syspara_verno:
                upd_flag = 1
            #更新标志
            data = struct.pack("!B", upd_flag)
            #心跳时间间隔
            data += struct.pack("!B", 8)
            #工作模式
            data += struct.pack("!B", 1)
        elif cmd_code == 0x07:
            self.print_words(u"收到下载时间段参数")
            data = "\x10\x00\x11\x00\x00"
            test_data = []
            for i in range(0, 32, 1):
                test_data.append(chr(0xFF))
            timepara_bitmap = "".join(test_data)
            data += timepara_bitmap
            data *= 4
        elif cmd_code == 0x08:
            upd_flag = 0
            self.print_words(u"收到更新黑名单")
            if self.blacklist_verno != recv_data:
                upd_flag = 1
            #更新标志
            data += struct.pack("!B", upd_flag)
            #版本号
            data += self.blacklist_verno
            #名单个数
            data += struct.pack(">H", 10)
            #名单列表
            for i in range(0, 10, 1):
                cardno = struct.pack(">I", i)
                data += cardno
        return data

    def do_something_with_data(self, s, fid):
        # print u"==============处理数据：============="
        # m_handler.print_data_list(fid)
        m_tcp_unt = sp_datalist.sp_tcp_unit()
        index = self.list_handler.get_index_by_fid(fid)
        if index < 0:
            return False
        data_valid_len = self.list_handler.data_list[index][1]
        data = self.list_handler.data_list[index][2]
        data = data[0:data_valid_len]
        # 解析数据
        gloabal_log_handler.sp_brief_log(data, FLAG_RECV)
        m_tcp_unt.parse_data(data)
        # print u"解析出data_len={0}".format(m_tcp_unt.data_len)
        m_tcp_unt.data = self.prepare_data_by_cmd(m_tcp_unt.cmd_code, m_tcp_unt.data, fid)
        m_tcp_unt.data_len = len(m_tcp_unt.data)
        data = m_tcp_unt.get_hd_buffer()
        s.send(data)
        gloabal_log_handler.sp_detail_log(data, FLAG_SEND)


    def handle_recv_data(self, s, buf):
        if len(buf) == FRAME_LENGTH:
            m_unt = sp_datalist.sp_trans_unit()
            m_unt.unpack_start_unit(buf)
            if self.list_handler.insert_into_list(s, m_unt, buf) == 2:
                # 处理接收到的请求，一般情况是转发并等待服务器回复
                print "\nget full fid={0} req".format(m_unt.fid)
                self.do_something_with_data(s, m_unt.fid)
                # 清空该fid对应的列表的数据
                self.list_handler.clear_list_elems(m_unt.fid)
        else:
            print u"长度不对！len={0}".format(len(buf))


    def process_buffer(self, client, recv_buffer):
        offset = 0
        process_length = 0
        buffer_len = len(recv_buffer)
        while offset < buffer_len:
            if buffer_len - offset >= FRAME_LENGTH:
                self.handle_recv_data(client, recv_buffer[offset: offset + FRAME_LENGTH])
                process_length += FRAME_LENGTH
            offset += FRAME_LENGTH
        return process_length
