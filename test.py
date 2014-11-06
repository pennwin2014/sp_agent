__author__ = 'Penn'


def sp_calc_crc8(data, len):
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

if __name__ == "__main__":
    deta = "\x48\x53\x56\x01\x21\x00\x00\x01\x04\x00\x00\x00\x00\x09\x00\x09\x00\x09\x00\x09"
    checksum2= sp_calc_crc8(deta, len(deta))
    data = "\x48\x53\x56\x01\x21\x00\x00\x01\x0a\x00\x00\x00\x00\x09\x00\x09\x00\x09\x00\x09"
    checksum = sp_calc_crc8(data, len(data))
    print "checksum={0:02x}, checksum2={1:02x}".format(checksum, checksum2)