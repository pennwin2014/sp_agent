# coding=utf-8
__author__ = 'Penn'

import sp_log_handler
import sp_datalist
import struct
import socket
import time
import binascii

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


def pack_test_data(cmd):
    result = ["HST", chr(cmd & 0xFF)]  # 引导码和命令码
    test_data = "123456"
    address = struct.pack("<H", 2)
    data_len = len(test_data) + len(address)
    data_len_byte = struct.pack('<H', data_len)
    result.append(data_len_byte)  # 数据包长度
    result.append(address)  # 机器地址
    result.append(test_data)  # 数据
    crc_data = "".join(result)
    crc = calc_check_sum(crc_data, len(crc_data))
    print "{0:02x}".format(crc)
    result.append(chr(crc))  # crc
    return "".join(result)


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
            svrtime = time.strftime('%y%m%d%H%M%S', time.localtime(time.time()))
            # 黑名单版本号
            self.blacklist_verno = binascii.unhexlify(svrtime)
            # 接收到的流水号
            self.recv_transdtl_no = 1
        # 系统参数版本号
        self.syspara_verno = 2
        # 费率版本号
        self.feerate_verno = 1
        # 时间段参数版本号
        self.timepara_verno = 3

    def handle_auth(self, auth_data, fid):
        print u"收到一次签到"
        """
        termno, soft_verno, cur_datetime, feerate_verno, syspara_verno = struct.unpack(AUTH_CPY_STR, auth_data)
        log_str = ""
        tmp_str = u"\ntermno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(termno[0]), ord(termno[1]), ord(termno[2]),
                                                                    ord(termno[3]))
        log_str += tmp_str
        tmp_str = u"\nsoft_verno={0:02x}{1:02x}{2:02x}\n".format(ord(soft_verno[0]), ord(soft_verno[1]),
                                                                 ord(soft_verno[2]))
        log_str += tmp_str
        tmp_str = u"\ncur_datetime={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}\n".format(ord(cur_datetime[0]),
                                                                                               ord(cur_datetime[1]),
                                                                                               ord(cur_datetime[2]),
                                                                                               ord(cur_datetime[3]),
                                                                                               ord(cur_datetime[4]),
                                                                                               ord(cur_datetime[5]),
                                                                                               ord(cur_datetime[6]))
        log_str += tmp_str
        tmp_str = u"\nfeerate_verno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(feerate_verno[0]), ord(feerate_verno[1]),
                                                                           ord(feerate_verno[2]), ord(feerate_verno[3]))
        log_str += tmp_str
        tmp_str = u"\nsyspara_verno={0:02x}{1:02x}{2:02x}{3:02x}\n".format(ord(syspara_verno[0]), ord(syspara_verno[1]),
                                                                           ord(syspara_verno[2]), ord(syspara_verno[3]))
        log_str += tmp_str
        path = u"auth_logs"
        gloabal_log_handler.sp_classify_log(path, log_str, fid)
        """

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
        self.print_words(u"收到一笔流水，transflag={0:02X}，termseqno={1}".format(transflag, termseqno))
        return termseqno

    def handle_trussdtl(self, trussdtl, fid):
        # print u"trussdtl_len={0}".format(len(trussdtl))
        trussno, trussdatetime, last_trussno, success_cnt, success_amt, fail_cnt, fail_amt, last_termseqno, end_termseqno, \
        start_transtime, end_transtime, reverse, crc = struct.unpack(TRUSSDTL_CPY_STR, trussdtl)
        log_str = ""
        tmp_str = u"\ntrussno={0}\n".format(trussno)
        log_str += tmp_str
        self.print_words(u"收到一笔扎帐流水，{0}".format(tmp_str))
        tmp_str = u"trussdatetime=[{0:02X}][{1:02x}][{2:02x}][{3:02x}][{4:02x}]\n".format(ord(trussdatetime[0]),
                                                                                          ord(trussdatetime[1]),
                                                                                          ord(trussdatetime[2]),
                                                                                          ord(trussdatetime[3]),
                                                                                          ord(trussdatetime[4]))
        log_str += tmp_str
        tmp_str = u"last_termseqno={0}\n".format(last_termseqno)
        log_str += tmp_str
        tmp_str = u"end_termseqno={0}\n".format(end_termseqno)
        log_str += tmp_str
        tmp_str = u"start_transtime=[{0:02X}][{1:02x}][{2:02x}][{3:02x}][{4:02x}][{5:02x}]\n".format(
            ord(start_transtime[0]), ord(start_transtime[1]),
            ord(start_transtime[2]), ord(start_transtime[3]), ord(start_transtime[4]), ord(start_transtime[5]))
        log_str += tmp_str
        tmp_str = u"end_transtime=[{0:02X}][{1:02x}][{2:02x}][{3:02x}][{4:02x}][{5:02x}]\n".format(
            ord(end_transtime[0]), ord(end_transtime[1]),
            ord(end_transtime[2]), ord(end_transtime[3]), ord(end_transtime[4]), ord(end_transtime[5]))
        log_str += tmp_str
        tmp_str = u"success_cnt={0}\n".format(success_cnt)
        log_str += tmp_str
        tmp_str = u"success_amt={0}\n".format(success_amt)
        log_str += tmp_str
        tmp_str = u"fail_cnt={0}\n".format(fail_cnt)
        log_str += tmp_str
        tmp_str = u"fail_amt={0}\n".format(fail_amt)
        log_str += tmp_str
        path = u"trussdtl_logs"
        gloabal_log_handler.sp_classify_log(path, log_str, fid)
        return trussno

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

    def get_data_from_server(self, send_data):
        host = "192.168.1.106"
        port = 9001
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        timeout = 60
        while timeout > 0:
            timeout -= 1
            s.send(send_data)
            data = s.recv(1024)
            if len(data) > 0:  # 后期再改成接收到完整的数据
                print u"收到后台应答数据:"
                self.print_can_data(data)
                break
            time.sleep(1)
        s.close()
        return data


    def prepare_data_by_cmd(self, cmd_code, recv_data, fid):
        data = ""
        self.prepare_verno()
        print "cmd={0:02x}".format(cmd_code)
        if cmd_code == 0x00:
            self.print_words(u"收到链路检测")
            data = "\x00\x01\x03"
        elif cmd_code == 0x09:  # 扎帐
            trussno = self.handle_trussdtl(recv_data, fid)
            self.recv_truss_no = trussno
            retcode = 0
            data = struct.pack("<BIs", retcode, trussno, '1')
        elif cmd_code == 0xD2:  # 交易流水
            termseqno = self.handle_transdtl(recv_data, fid)
            self.recv_transdtl_no = termseqno
            retcode = 0
            data = struct.pack("<BIs", retcode, termseqno, '1')
        elif cmd_code == 0xE1:  # 签到
            self.handle_auth(recv_data, fid)
            import time
            svrtime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            import binascii
            # 返回码
            send_data = struct.pack(">I", 0)
            # 启用状态
            send_data += "\x01"
            # 系统时钟
            send_data += binascii.unhexlify(svrtime)
            # 商户号
            send_data += struct.pack(">I", 0)
            # 设备终端编号
            devphyid = "00000011"
            send_data += binascii.unhexlify(devphyid)
            # 设备id
            send_data += struct.pack(">I", 1)
            #费率版本号
            send_data += struct.pack(">I", self.feerate_verno)
            #主参数版本
            send_data += struct.pack(">I", self.syspara_verno)
            #时间段参数版本
            send_data += struct.pack(">I", self.timepara_verno)
            #黑名单版本号
            send_data += self.blacklist_verno
            #m1卡密钥
            m1_key = "3132333431323334"
            send_data += binascii.unhexlify(m1_key)
            #参数组id
            send_data += struct.pack(">I", 1)
            #keyindex
            send_data += "\x01"
            data = send_data
        elif cmd_code == 0xE2:
            self.print_words(u"收到心跳")
            # 解析接收到的心跳数据
            pos_time, pos_send_transno, pos_transno = struct.unpack("!6sII", recv_data)
            # 黑名单版本号
            send_data = self.blacklist_verno
            # 主系统参数版本号
            send_data += struct.pack(">I", self.syspara_verno)
            # 费率表版本号
            send_data += struct.pack(">I", self.feerate_verno)
            # 时间段参数版本号
            send_data += struct.pack(">I", self.timepara_verno)
            #已接收到的流水号
            send_data += struct.pack(">I", self.recv_transdtl_no)
            #当前流水号
            send_data += struct.pack(">I", pos_transno)
            #pos机时间
            send_data += pos_time
            data = send_data
        elif cmd_code == 0xE3:
            self.print_words(u"收到获取黑名单请求")
            self.print_can_data(recv_data)
            max_page_cnt = 10
            index = struct.unpack("<H", recv_data)
            index = index[0]
            print u"收到index={0}".format(index)
            index += 1
            end_flag = 0
            if index > max_page_cnt:
                end_flag = 1
            # 当前序号
            data += struct.pack(">H", index)
            # 是否结束
            data += struct.pack("B", end_flag)
            # 本次的字节数
            data += struct.pack(">H", 128)
            # 准备黑名单位图 128*10
            test_data = []
            for i in range(0, 128, 1):
                test_data.append(chr(0xFF))
            blacklist_bitmap = "".join(test_data)
            data += blacklist_bitmap
        elif cmd_code == 0xE4:
            upd_flag = 0
            self.print_words(u"收到更新黑名单")
            if self.blacklist_verno != recv_data:
                upd_flag = 1
            # 更新标志
            data += struct.pack("!B", upd_flag)
            # 版本号
            data += self.blacklist_verno
            # 名单个数
            data += struct.pack(">H", 10)
            # 名单列表
            for i in range(0, 10, 1):
                cardno = struct.pack(">I", i)
                data += cardno
        elif cmd_code == 0xE5:
            self.print_words(u"收到下载主参数")
            # 主参数版本号
            pos_syspara_verno = struct.unpack(">I", recv_data)
            pos_syspara_verno = pos_syspara_verno[0]
            upd_flag = 0
            if pos_syspara_verno != self.syspara_verno:
                upd_flag = 1
            # 更新标志
            data = struct.pack("!B", upd_flag)
            # 心跳时间间隔
            data += struct.pack("!B", 8)
            # 工作模式
            data += struct.pack("!B", 1)
            # 系统时钟
            import time

            svrtime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
            import binascii

            data += binascii.unhexlify(svrtime)
            #扎帐点,各两个字节
            data += "\x09\x12"
            data += "\x14\x30"
            data += "\x17\x50"
        elif cmd_code == 0xE6:
            self.print_words(u"收到下载时间段参数")
            data = "\x10\x00\x11\x00\x00"
            test_data = []
            for i in range(0, 32, 1):
                test_data.append(chr(0xFF))
            timepara_bitmap = "".join(test_data)
            data += timepara_bitmap
            data *= 4
        elif cmd_code == 0xE7:
            self.print_words(u"收到下载费率表请求")
            test_data = []
            for i in range(0, 256, 1):
                test_data.append(chr(120))
            feerate_table = "".join(test_data)
            data = feerate_table
            # 允许使用卡类别位图
            test_data = []
            for i in range(0, 32, 1):
                test_data.append(chr(0xFF))
            feetype_bitmap = "".join(test_data)
            data += feetype_bitmap
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
        """
        m_tcp_unt.data = self.prepare_data_by_cmd(m_tcp_unt.cmd_code, m_tcp_unt.data, fid)
        """
        send_data = self.translate_to_sw_agent_fmt(m_tcp_unt)
        recv_data = self.get_data_from_server(send_data)
        m_tcp_unt.data = self.translate_to_pos_fmt(recv_data)
        m_tcp_unt.canid = fid
        print u"\n将后台数据翻译后：cmd={0:02x}, c长度={1}".format(m_tcp_unt.cmd_code, len(m_tcp_unt.data))
        self.print_can_data(m_tcp_unt.data)
        m_tcp_unt.data_len = len(m_tcp_unt.data)
        data = m_tcp_unt.get_hd_buffer()
        # s.send(data)
        s.send_message(data)
        gloabal_log_handler.sp_detail_log(data, FLAG_SEND)


    def handle_recv_data(self, s, buf):
        if len(buf) == FRAME_LENGTH:
            m_unt = sp_datalist.sp_trans_unit()
            #都当作首帧来解析
            m_unt.unpack_start_unit(buf)
            if self.list_handler.insert_into_list(s, m_unt, buf) == 2:
                # 处理接收到的请求，一般情况是转发并等待服务器回复
                import datetime
                now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
                print u"\n得到完整fid=0x{0:02x}数据时间：{1}".format(m_unt.fid, now_time)
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
