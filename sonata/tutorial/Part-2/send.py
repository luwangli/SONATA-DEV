from scapy.all import *
import os
import sys
import glob
import math, time
import pickle
from multiprocessing.connection import Listener

NORMAL_PACKET_COUNT = 15
ATTACK_PACKET_COUNT = 15

IFACE = "out-veth-1"

resolverIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))


def create_normal_traffic():
    number_of_packets = NORMAL_PACKET_COUNT
    normal_packets = []

    for i in range(number_of_packets):
        sIP = resolverIP
        dIP = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        rdata = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        p = Ether() / IP(dst=dIP, src=sIP) / UDP(sport=53) /DNS(qr=1, aa=1, ancount=1,an=DNSRR(rdata=rdata))
        normal_packets.append(p)

    return normal_packets


def create_iot_traffic():
    number_of_packets = ATTACK_PACKET_COUNT
    dIP = '99.7.186.25'
    sIPs = []
    attack_packets = []

    for i in range(number_of_packets):
        sIPs.append(resolverIP)

    for sIP in sIPs:
        p = Ether() / IP(dst=dIP, src=sIP) / UDP(sport=53) /DNS(qr=1, aa=1, ancount=1,an=DNSRR(rrname='www.iot-device.com', rdata='192.168.1.1'))
        attack_packets.append(p)

    return attack_packets


def send_created_traffic():
    traffic_dict = {}
    attack = True

    total_duration = 30
    attack_duration = 15
    attack_start_time = 5

    for i in range(0, total_duration):
        traffic_dict[i] = []
        traffic_dict[i].extend(create_normal_traffic())
        if i >= attack_start_time and i < attack_start_time + attack_duration:
            traffic_dict[i].extend(create_iot_traffic())

    print "******************** Sending Normal Traffic *************************"
    for i in range(0, total_duration):
        # print "Sending traffic for ts: " + str(i)
        start = time.time()
        if i >= attack_start_time and i < attack_start_time + attack_duration and attack:
            attack = False
            print "******************** Sending IoT Traffic *************************"
        if i == attack_start_time + attack_duration:
            attack = False

        if not attack and i > attack_start_time + attack_duration:
            attack = True
            print "******************** Sending Normal Traffic *************************"

        sendp(traffic_dict[i], iface=IFACE, verbose=0)
        total = time.time() - start
        sleep_time = 1 - total
        if sleep_time > 0:
            time.sleep(sleep_time)

send_created_traffic()
