# coding=utf-8
__author__ = 'Penn'

import sp_log_handler
import sp_datalist
import struct

FRAME_LENGTH = 16
DATA_HEADER_CPY_STR = "<3sBH2sI"
DATA_HEADER_LEN = 12
TRANSDTL_CPY_STR = "<IIH3sIB6s6sIHI3s6s6s4sB2s2s"  # "IIH3sIB6s6sIBI3s6s6s4sB2s2s144s"
FLAG_SEND = True
FLAG_RECV = False
gloabal_log_handler = sp_log_handler.sp_log_handler()


class sp_hd_handler():
    def __init__(self):
        list_handler = sp_datalist.sp_datalist_handler()
        recieved_buffer = ""


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
        gloabal_log_handler.sp_transdtl_log(log_str, fid)
        tmp_str = u"amount={4},tac={0:02X}{1:02X}{2:02X}{3:02X}".format(ord(tac[0]), ord(tac[1]), ord(tac[2]),
                                                                        ord(tac[3]), amount)
        # print tmp_str
        tmp_str = u"收到一笔流水，transflag={0:02X}".format(transflag)
        print tmp_str
        return termseqno



    def print_can_data(self, data):
        import time

        print u"{0}  data=".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))),
        for i in range(0, len(data)):
            print "{0:02x}".format(ord(data[i])),


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
        if m_tcp_unt.cmd_code == 0x01:
            termseqno = self.handle_transdtl(m_tcp_unt.data, fid)
            m_tcp_unt.data = struct.pack("<BI", 6, termseqno)
        elif m_tcp_unt.cmd_code == 0x02:
            self.print_can_data(m_tcp_unt.data)
            m_tcp_unt.data = "\x00\x09\x00\x09\x00\x09\x00\x09"
        elif m_tcp_unt.cmd_code == 0x03:
            print u"收到获取黑名单请求,len={0}".format(m_tcp_unt.data_len)
            m_tcp_unt.data = "\x00\x09\x00\x09\x00\x09\x00\x09"
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
