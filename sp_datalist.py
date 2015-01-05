# coding=utf-8
import sys, struct, socket
import sp_log_handler

FRAME_LENGTH = 16
DATA_HEADER_CPY_STR = "<3sBH2sI"
DATA_HEADER_LEN = 12
TRANSDTL_CPY_STR = "<IIH3sIB6s6sIHI3s6s6s4sB2s2s"  # "IIH3sIB6s6sIBI3s6s6s4sB2s2s144s"
FLAG_SEND = True
FLAG_RECV = False
gloabal_log_handler = sp_log_handler.sp_log_handler()


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
            kd1, self.flen, kd2, self.fid, self.fchecksum, \
            self.findex, self.fdata = struct.unpack("!sB2sI2B6s", recv_data)

    def unpack_start_unit(self, recv_data):
        if len(recv_data) != FRAME_LENGTH:
            print "unpack_start_unit len={0}".format(len(recv_data))
        else:
            keep_data1, self.flen, keep_data2, self.fid, self.fchecksum, \
            self.findex, self.fdatalen, self.fdata = struct.unpack("<sB2s4s2B2s4s", recv_data)
            self.fid = struct.unpack(">I", self.fid)[0]
            print "\n收到数据"
            for x in recv_data:
                print "{0:02x}".format(ord(x)),
            print "本次帧长度={0},fid=0x{1:02x},findex={2}".format(self.flen, self.fid, self.findex)


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
        import datetime
        print "\n"+"="*80+"\n"
        print u"收到fid=0x{0:02x}第一帧时间：{1}".format(fid, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")),
        index = self.get_index_by_fid(fid)
        if index < 0:
            return 1  # 该帧id对应的列表不存在
        total_len = struct.unpack('<H', fdatalen)[0]
        print u"数据长度=[{0}]".format(total_len)
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


    def insert_into_list(self, pass_unt, buf):
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
        if ret != 2:
            self.data_list[index].append(buf)
        return ret


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
            gloabal_log_handler.print_hex(self.data_list[index][2])
            print u"总数据长度:{0}, 有效数据长度:{1}".format(len(self.data_list[index][2]), self.data_list[index][1])
        else:
            print u"该fid不存在列表！"


    def get_real_data(self, fid):
        index = self.get_index_by_fid(fid)
        if index < 0:
            return None
        m_str = self.data_list[index][2]
        return m_str


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
        #print "data_len = {0}".format(self.data_len)
        self.data = data[DATA_HEADER_LEN:DATA_HEADER_LEN + self.data_len]

        print "data=",
        for i in range(0, self.data_len):
            print "{0:02x}".format(ord(self.data[i])),

        self.check_sum = data[DATA_HEADER_LEN + self.data_len]
        #print "\nchecksum={0:02x}".format(ord(self.check_sum))


    @staticmethod
    def get_check_sum(data, frame_index):
        tmp_sum = frame_index
        for x in data:
            tmp_sum ^= ord(x)
        check_sum = struct.pack('B', tmp_sum)
        return check_sum

    def sp_calc_crc8(self, data, len):
        i = 0
        crc = 0
        cnt = 0
        while len > 0:
            len -= 1
            crc ^= ord(data[cnt])
            cnt += 1
            for i in range(0, 8, 1):
                if crc & 0x01 != 0:
                    crc = (crc >> 1) ^ 0x8C
                else:
                    crc >>= 1
        return crc

    def pack_one_frame(self, frame_len, check_sum, frame_index, data):
        #pack_data = struct.pack(">sH2sIBB"+len(data)+"s"+FRAME_LENGTH-len(data)-10+"s")
        #
        pack_data = struct.pack("B", 0)
        pack_data += struct.pack(">B", frame_len + 2)
        pack_data += struct.pack(">H", 0)
        pack_data += struct.pack(">I", self.canid)
        pack_data += check_sum
        findex = struct.pack("B", frame_index)
        pack_data += findex
        pack_data += data
        while len(pack_data) < FRAME_LENGTH:
            pack_data += "\x00"
        return pack_data


    def get_hd_buffer(self):
        """
        data = '\x12\x23\x33\x44\x55\x66\x77\x88\x99\xAA\xBB\xCC\xDD\xEE\xFF\x12\x34\x56\x78\x9A\xBC\xDE\xF0'
        data *= 23
        print "check_sum={0:02x}".format(ord(self.check_sum))
        """
        data = struct.pack(DATA_HEADER_CPY_STR, self.guide_code, self.cmd_code, self.data_len, self.machine_addr,
                           self.seqno)
        data += self.data
        """
        for i in range(0, len(data), 1):
            print "\\x{0:02x}".format(ord(data[i])),
        """
        self.check_sum = self.sp_calc_crc8(data, len(data))
        #print "check_sum2={0:02x}".format(self.check_sum)
        pack_str = "<{0}sB".format(len(data))
        data = struct.pack(pack_str, data, self.check_sum)
        gloabal_log_handler.sp_brief_log(data, FLAG_SEND)  # 记录发送日志
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


"""
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
"""
