# coding=utf-8
__author__ = 'Penn'

import sp_log_handler
import sp_datalist
import struct

FRAME_LENGTH = 16
DATA_HEADER_CPY_STR = "<3sBH2sI"
DATA_HEADER_LEN = 12
TRANSDTL_CPY_STR = "<IIH3sIB6s6sIHI3s6s6s4sB2s2s"  # "IIH3sIB6s6sIBI3s6s6s4sB2s2s144s"
TRUSSDTL_CPY_STR = "<I5sIIIIIII6s6s13s2s"
AUTH_CPY_STR = "<4s3s7s4s4s"
FLAG_SEND = True
FLAG_RECV = False
gloabal_log_handler = sp_log_handler.sp_log_handler()
global_cnt = 1


def calc_check_sum(check_data, check_len):
    tmp_sum = 0
    for i in range(0, check_len, 1):
        tmp_sum += ord(check_data[i])
    tmp_result = tmp_sum
    tmp_result = (~tmp_result) & 0xFF
    return tmp_result


class sp_hd_handler():
    def __init__(self):
        list_handler = sp_datalist.sp_datalist_handler()
        recieved_buffer = ""

    @staticmethod
    def print_words(words):
        import datetime
        print u"{0}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        print words

    def print_can_data(self, data):
        self.print_words("data=")
        for i in range(0, len(data)):
            print "{0:02x}".format(ord(data[i])),

    def translate_to_pos_fmt(self, recv_data):
        # 53 4c 56 e1 2f 00 02 00 00 20 14 12 18 15 58 08 00 00 00 14 00 00 00 00 00 00 00 00 00 00 00 3e 00 00 00 3e 00 00 00 3e 32 30 30 35 30 31 33 31 00 00 00 01 01 c9
        """
        引导码 命令码 数据包长度 机器地址 数据信息 校验
        """
        dd = recv_data[4:6]
        data_len = struct.unpack("<H", dd)[0]
        # print "data_len={0}".format(data_len)
        data_len -= 2
        fmt_str1 = "8s"
        fmt_str2 = "s1s"
        fmt_pack_str = "%s%d%s" % (fmt_str1, data_len, fmt_str2)
        header, data, crc = struct.unpack(fmt_pack_str, recv_data)
        return data

    def translate_to_sw_agent_fmt(self, m_unit):
        # 去掉seqno再组一个包
        result = ["HST", chr(m_unit.cmd_code & 0xFF)]  # 引导码和命令码
        address = struct.pack("<H", 2)  # m_unit.machine_addr)
        data_len = len(m_unit.data) + len(address)
        data_len_byte = struct.pack('<H', data_len)
        #print "data_len={0}".format(data_len)
        result.append(data_len_byte)  # 数据包长度
        result.append(address)  # 机器地址
        result.append(m_unit.data)  # 数据
        crc_data = "".join(result)
        crc = calc_check_sum(crc_data, len(crc_data))
        #print "{0:02x}".format(crc)
        result.append(chr(crc))  # crc
        return "".join(result)

    def get_data_from_server(self, server,client, send_data,unt):
        data = client.fetch(server,send_data,unt);
        return data

    def do_something_with_data(self, server,client, fid):
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
        send_data = self.translate_to_sw_agent_fmt(m_tcp_unt)
        print send_data
        self.get_data_from_server(server,client,send_data,m_tcp_unt)


    def handle_recv_data(self, server,client, buf):
        if len(buf) == FRAME_LENGTH:
            m_unt = sp_datalist.sp_trans_unit()
            m_unt.unpack_start_unit(buf)
            if self.list_handler.insert_into_list(m_unt, buf) == 2:
                # 处理接收到的请求，一般情况是转发并等待服务器回复
                print "\nget full fid={0} req".format(m_unt.fid)
                self.do_something_with_data(server,client, m_unt.fid)
                # 清空该fid对应的列表的数据
                self.list_handler.clear_list_elems(m_unt.fid)
        else:
            print u"长度不对！len={0}".format(len(buf))


    def process_buffer(self, server, client, recv_buffer):
        offset = 0
        process_length = 0
        buffer_len = len(recv_buffer)
        while offset < buffer_len:
            if buffer_len - offset >= FRAME_LENGTH:
                self.handle_recv_data(server, client, recv_buffer[offset: offset + FRAME_LENGTH])
                process_length += FRAME_LENGTH
            offset += FRAME_LENGTH
        return process_length
