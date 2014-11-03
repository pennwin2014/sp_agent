# coding=utf-8
import sys, struct, socket
import datetime
import os

FRAME_LENGTH = 16


class sp_trans_unit:
    def __init__(self):
        self.flen = 0
        self.fid = 0
        self.fchecksum = 0
        self.findex = 0
        self.fdatalen = "\x01\x02"  # 只有第一个包有
        self.fdata = "\x01\x02\x03\x04\x05\x06"


    def unpack_normal_unit(self, recv_data):
        if len(recv_data) != FRAME_LENGTH:
            print "unpack_normal_unit len={0}".format(len(recv_data))
        else:
            self.flen, self.fid, self.fchecksum, \
            self.findex, self.fdata = struct.unpack("!2I2B6s", recv_data)

    def unpack_start_unit(self, recv_data):
        if len(recv_data) != FRAME_LENGTH:
            print "unpack_start_unit len={0}".format(len(recv_data))
        else:
            self.flen, self.fid, self.fchecksum, \
            self.findex, self.fdatalen, self.fdata = struct.unpack("<2I2B2s4s", recv_data)


class sp_datalist_handler:
    def __init__(self):
        self.data_list = []


    def get_index_by_fid(self, fid):
        for i in range(0, len(self.data_list), 1):
            if self.data_list[i][0] == fid:
                return i
        return -1


    def create_new_list(self, fid):
        if self.get_index_by_fid(fid) >= 0:
            print u"已存在"
            return False
        self.data_list.append([])
        self.data_list[len(self.data_list) - 1].append(fid)
        return True


    def append_first_data(self, fid, fdatalen, fdata):
        index = self.get_index_by_fid(fid)
        if index < 0:
            return 1  # 该帧id对应的列表不存在
        total_len = struct.unpack('<H', fdatalen)[0]
        total_data = fdata
        self.data_list[index] = [fid, total_len, total_data]
        if total_len == 4:
            return 2
        else:
            return 0


    def append_normal_data(self, fid, fdata):
        index = self.get_index_by_fid(fid)
        if index < 0:
            return 1  # 该帧id对应的列表不存在
        total_len = self.data_list[index][1]
        self.data_list[index][2] += fdata
        if len(self.data_list[index][2]) == total_len:
            return 2
        elif len(self.data_list[index][2]) > total_len:
            # print u"接收到的数据总数超过首帧设定的总数"
            return 2
        return 0  # 未接收完整个请求


    def insert_into_list(self, s, pass_unt, buf):
        index = self.get_index_by_fid(pass_unt.fid)
        if index < 0:
            self.create_new_list(pass_unt.fid)
        if pass_unt.findex == 0:  # 帧序号为0，即第一帧
            # 记录下数据长度以及数据，如果帧长度只有一个帧，则处理该数据并清空列表
            ret = self.append_first_data(pass_unt.fid, pass_unt.fdatalen, pass_unt.fdata)
        else:
            # 如果数据长度拼起来是最后一个，则处理该数据并清空列表
            pass_unt.unpack_normal_unit(buf)
            ret = self.append_normal_data(pass_unt.fid, pass_unt.fdata)
        if ret == 2:  # 最后一个帧
            do_something_with_data(s, self, pass_unt.fid)
            self.clear_list_elems(pass_unt.fid)
        else:
            self.data_list[index].append(buf)


    def clear_list_elems(self, fid):
        index = self.get_index_by_fid(fid)
        if index < 0:
            print u"列表不存在"
            return False
        self.data_list[index] = [fid]
        return True


    def print_data_list(self, fid):
        index = self.get_index_by_fid(fid)
        if index >= 0:
            print u"该列表元素个数={0}".format(len(self.data_list[index]))
            print self.data_list[index]
            print u"接收到的数据："
            print_hex(self.data_list[index][2])
            print u"总数据长度:{0}, 有效数据长度:{1}".format(len(self.data_list[index][2]), self.data_list[index][1])
        else:
            print u"该fid不存在列表！"


    def get_real_data(self, fid):
        index = self.get_index_by_fid(fid)
        if index < 0:
            return None
        m_str = self.data_list[index][2]
        return m_str


# DATA_CPY_STR = "<3sBH2s207sB"
DATA_HEADER_CPY_STR = "<3sBH2sI"
DATA_HEADER_LEN = 12

TRANSDTL_CPY_STR = "<IIH3sIB6s6sIHI3s6s6s4sB2s2s"  # "IIH3sIB6s6sIBI3s6s6s4sB2s2s144s"


class sp_tcp_unit:
    def __init__(self):
        self.guide_code = '\x00\x00\x00'  # 引导码
        self.cmd_code = '\x00'  # 命令码
        self.data_len = 10  # 数据长度
        self.machine_addr = '\x00\x01'  # 机器地址
        self.seqno = 1
        self.data = ''
        self.check_sum = '\x08'
        self.canid = "\x00\x00\x00\x00"

    def parse_data(self, data):
        self.guide_code, self.cmd_code, self.data_len, self.machine_addr, self.seqno = struct.unpack(
            DATA_HEADER_CPY_STR, data[0:DATA_HEADER_LEN])
        print "parse data_len = {0}".format(self.data_len)
        self.data = data[DATA_HEADER_LEN:DATA_HEADER_LEN + self.data_len]
        print "data=[{0:02x}{1:02x}{2:02x}{3:02x}{4:02x}]".format(ord(self.data[0]), ord(self.data[1]),
                                                                  ord(self.data[2]), ord(self.data[3]),
                                                                  ord(self.data[4]))
        self.check_sum = data[DATA_HEADER_LEN + self.data_len]
        print "checksum={0:02x}".format(ord(self.check_sum))
        """
        self.guide_code, self.cmd_code, self.data_len, self.machine_addr, self.data, self.check_sum = struct.unpack(
            DATA_CPY_STR, data)
        """

    @staticmethod
    def get_check_sum(data, frame_index):
        tmp_sum = frame_index
        for i in range(0, len(data), 1):
            tmp_sum ^= ord(data[i])
        check_sum = struct.pack('B', tmp_sum)
        return check_sum


    def pack_one_frame(self, frame_len, check_sum, frame_index, data):
        pack_data = struct.pack(">H", frame_len + 2)
        pack_data += "\x00\x00"
        pack_data += self.canid
        pack_data += check_sum
        findex = struct.pack("B", frame_index)
        pack_data += findex
        pack_data += data
        while len(pack_data) < FRAME_LENGTH:
            pack_data += "\x00"
        return pack_data


    def get_hd_buffer(self):
        data = '\x12\x23\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF\x12\x34\x56\x78\x9A\xBC\xDE\xF0'
        data *= 23
        """
        data = struct.pack(DATA_HEADER_CPY_STR, self.guide_code, self.cmd_code, self.data_len, self.machine_addr, self.seqno)
        data += self.data
        data += self.check_sum
        """
        sp_brief_log(data, True)#记录发送日志
        # print u"组第一个帧前LEN= {0}".format(len(data))
        tmp_data = struct.pack("<H", len(data))
        tmp_data += data[0:4]
        check_sum = self.get_check_sum(tmp_data, 0)
        pack_data = self.pack_one_frame(len(tmp_data), check_sum, 0, tmp_data)
        data = data[4:len(data)]
        # print u"组完第一个帧后LEN= {0}".format(len(data))
        frame_index = 1
        if len(data) > 6:
            for i in range(0, len(data), 6):
                tmp_data = data[i:i + 6]
                # print u"i={0},len(tmp_data)={1}".format(i, len(tmp_data))
                check_sum = self.get_check_sum(tmp_data, frame_index)
                pack_data += self.pack_one_frame(len(tmp_data), check_sum, frame_index, tmp_data)
                frame_index += 1
        # print "=======pack_data====="
        # print_hex(pack_data)
        return pack_data


def sp_transdtl_log(transdtl, fid):
    path = u"transdtl_logs"
    # title = u"{0}".format(datetime.date.today())
    #new_path = os.path.join(path, title)
    #sub_title = u"transdtl_logs"
    #new_path = os.path.join(new_path, sub_title)
    new_path = path
    if not os.path.isdir(new_path):
        os.makedirs(new_path)
    fileHandler = open(
        new_path + "\\{0}.log".format(datetime.date.today()), 'a')
    fileHandler.write("====================\ntime={0:02d}:{1:02d}:{2:02d}, fid={3}\n=================={4}\n".format(
        datetime.datetime.now().hour, datetime.datetime.now().minute,
        datetime.datetime.now().second, fid, transdtl))
    fileHandler.close()


def sp_brief_log(m_str, issend):
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


def sp_detail_log(m_str, issend):
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


def print_hex(m_str):
    for i in range(0, len(m_str), 1):
        print "{0:02X},".format(ord(m_str[i])),


def handle_transdtl(transdtl, fid):
    # print u"transdtl_len={0}".format(len(transdtl))
    termseqno, cardno, lastcnt, lastlimamt, lastamount, lasttransflag, lasttermno, lastdatetime, cardbefbal, cardbefcnt, amount, \
    extraamount, transdatetime, psamno, tac, transflag, reserve, crc = struct.unpack(TRANSDTL_CPY_STR, transdtl)
    log_str = ""
    tmp_str = u"\ntermseqno={0}\ncardno={1}\nlastcnt={2}\n".format(termseqno, cardno, lastcnt)
    log_str += tmp_str
    tmp_str = u"lastlimamt=[{0:02X}][{1:02x}][{2:02x}]\n".format(ord(lastlimamt[0]), ord(lastlimamt[1]),
                                                                 ord(lastlimamt[2]))
    log_str += tmp_str
    tmp_str = u"lasttransflag={0:02x}\nlasttermno={1:02x}{2:02x}{3:02x}{4:02x}{5:02x}{6:02x}\n".format(lasttransflag,
                                                                                                       ord(lasttermno[
                                                                                                           0]), \
                                                                                                       ord(lasttermno[
                                                                                                           1]), ord(
            lasttermno[2]), ord(lasttermno[3]), ord(lasttermno[4]), ord(lasttermno[5]))
    log_str += tmp_str
    tmp_str = u"lastdatetime={0:02x}{1:02x}{2:02x}{3:02x}{4:02x}{5:02x}\n".format(ord(lastdatetime[0]),
                                                                                  ord(lastdatetime[1]),
                                                                                  ord(lastdatetime[2]), \
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
                                                                            ord(psamno[2]), ord(psamno[3]),
                                                                            ord(psamno[4]), ord(psamno[5]))
    log_str += tmp_str
    tmp_str = u"tac={0:02x}{1:02x}{2:02x}{3:02x}\ntransflag={4:02x}\nreserve={5:02x}{6:02x}\ncrc={7:02x}{8:02x}\n".format(
        ord(tac[0]), ord(tac[1]), ord(tac[2]), ord(tac[3]),
        transflag, ord(reserve[0]), ord(reserve[1]), ord(crc[0]), ord(crc[1]))
    log_str += tmp_str
    sp_transdtl_log(log_str, fid)
    #打印
    tmp_str = u"amount={4},tac={0:02X}{1:02X}{2:02X}{3:02X}".format(ord(tac[0]), ord(tac[1]), ord(tac[2]), ord(tac[3]),
                                                                    amount)
    #print tmp_str
    tmp_str = u"收到一笔流水，transflag={0:02X}".format(transflag)
    print tmp_str


def print_can_data(data):
    import time

    print u"{0}  {1}".format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), data)


def do_something_with_data(s, m_handler, fid):
    # print u"==============处理数据：============="
    # m_handler.print_data_list(fid)
    m_tcp_unt = sp_tcp_unit()
    index = m_handler.get_index_by_fid(fid)
    if index < 0:
        return False
    data_valid_len = m_handler.data_list[index][1]
    data = m_handler.data_list[index][2]
    data = data[0:data_valid_len]
    # print u"截取后的数据"
    # print_hex(data)
    # 解析数据
    sp_brief_log(data, False)
    m_tcp_unt.parse_data(data)
    #print u"解析出data_len={0}".format(m_tcp_unt.data_len)
    if m_tcp_unt.cmd_code == 0x01:
        handle_transdtl(m_tcp_unt.data, fid)
    elif m_tcp_unt.cmd_code == 0x02:
        print_can_data(m_tcp_unt.data)
    elif m_tcp_unt.cmd_code == 0x03:
        print u"收到获取黑名单请求,len={0}".format(m_tcp_unt.data_len)
    m_tcp_unt.data = "\x00\x09\x00\x09\x00\x09\x00\x09"
    m_tcp_unt.data_len = m_tcp_unt.data_len / 2 + 1
    data = m_tcp_unt.get_hd_buffer()
    s.send(data)
    sp_detail_log(data, True)


def handle_recv_data(s, m_handler, buf):
    if len(buf) == FRAME_LENGTH:
        m_unt = sp_trans_unit()
        m_unt.unpack_start_unit(buf)
        m_handler.insert_into_list(s, m_unt, buf)
    else:
        print u"长度不对！len={0}".format(len(buf))


def process_buffer(client, buffer, handler):
    offset = 0
    process_length = 0
    buffer_len = len(buffer)
    while offset < buffer_len:
        if buffer_len - offset >= FRAME_LENGTH:
            handle_recv_data(client, handler, buffer[offset: offset + FRAME_LENGTH])
            process_length += FRAME_LENGTH
        offset += FRAME_LENGTH
    return process_length


def recv_from_pos():
    host = "192.168.1.211"
    port = 6000
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    m_handler = sp_datalist_handler()
    recieved_buffer = ""
    while 1:
        buf = s.recv(1024)
        if not buf:
            print u"buf 长度不为16或者16的倍数，为{0}".format(len(buf))
            break
        recieved_buffer += buf
        process_length = process_buffer(s, recieved_buffer, m_handler)
        if process_length > 0:
            recieved_buffer = recieved_buffer[process_length:]
    s.close()


if __name__ == "__main__":
    recv_from_pos()

