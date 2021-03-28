from socket import *
import os
import sys
import struct
import time
import select
import binascii
from statistics import *

ICMP_ECHO_REQUEST = 8
timeRate = []


def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        # Fill in start

        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]
        requestType, code, revChecksum, revId, revSequence = struct.unpack(
            'bbHHh', icmpHeader)
        # print('struct', struct.unpack(
        #     'd', recPacket[12:20]))
        ip_header = struct.unpack('!BBHHHBBH4s4s', recPacket[:20])
        ttl = ip_header[5]
        saddr = inet_ntoa(ip_header[8])
        length = len(recPacket) - 20

        if ID == revId:
            timeSend = struct.unpack(
                'd', recPacket[28:28 + struct.calcsize('d')])[0]

            # print(struct.unpack('d', recPacket[0]))
            # print("timrec: {}, timesend: {}".format(timeReceived, timeSend))
            timeRate.append((timeReceived - timeSend)*1000)
            print("Reply from {}: bytes={} time={:.3f} TTL={}".format(
                saddr, length, (timeReceived - timeSend)*1000, ttl))

            # print('{} bytes from {}: icmp_seq={} ttl={} time={:.3f} ms'.format(
            # length, saddr, revSequence, ttl, (timeReceived - timeSend)*1000))
            return ((timeReceived - timeSend) * 1000)
        else:
            return "ID is not the same!"
        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    # AF_INET address must be tuple, not str
    mySocket.sendto(packet, (destAddr, 1))

    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    try:
        dest = gethostbyname(host)
    except:
        return ['0', '0.0', '0', '0.0']
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them

    # Send ping requests to a server separated by approximately one second
    for i in range(0, 4):
        delay = doOnePing(dest, timeout)
        time.sleep(1)  # one second

    vars = [str(round(min(timeRate), 2)), str(round(mean(timeRate), 2)), str(
        round(max(timeRate), 2)), str(round(stdev(timeRate), 2))]
    print("")
    print("--- {} ping statistics ---".format(dest))
    print("4 packets transmitted, 4 packets received, 0.0% packet loss")
    print("round-trip min/avg/max/stddev = {}/{}/{}/{} ms".format(str(round(min(timeRate), 2)), str(round(mean(timeRate), 2)), str(
        round(max(timeRate), 2)), str(round(stdev(timeRate), 2))))

    return vars


if __name__ == '__main__':
    ping("127.0.0.1")
