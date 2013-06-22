import array
import fcntl
import nmap
import requests
import socket
import struct

SIOCGIFNETMASK = 0x891b


def get_all_interfaces():
    max_possible = 128  # arbitrary. raise if needed.
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,  # SIOCGIFCONF
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()
    interfaces = list()
    for i in range(0, outbytes, 40):
        ifname = namestr[i:i + 16].split('\0', 1)[0]
        raw_netmask = fcntl.ioctl(s, SIOCGIFNETMASK, struct.pack('256s', ifname))[20:24]
        netmask_bin = str()
        for octet in raw_netmask:
            netmask_bin += bin(ord(octet))[2:].zfill(8)
        prefix = netmask_bin.count('1')
        raw_ip = namestr[i + 20: i + 24]
        netmask = socket.inet_ntoa(raw_netmask)
        ip = socket.inet_ntoa(raw_ip)
        network_addr = []
        for pair in zip(raw_ip, raw_netmask):
            network_addr.append(ord(pair[0]) & ord(pair[1]))
            network = '.'.join([str(i) for i in network_addr])
        interfaces.append({'ifname': ifname,
                           'ip': ip,
                           'netmask': netmask,
                           'prefix': prefix,
                           'network': network})
    return interfaces


CAMERA_PORT = 99  # Port by default


def scan_networks():
    nm = nmap.PortScanner()
    local_interfaces = list()
    cameras = list()
    for intf in get_all_interfaces():
        ifname, network, netmask = intf['ifname'], intf['network'], intf['netmask']
        if intf['ip'] == '127.0.0.1':
            print 'Interface: %s / %s / %s --> skipped' % (ifname, network, netmask)
        else:
            print 'Interface: %s / %s / %s' % (ifname, network, netmask)
            local_interfaces.append(intf)
    arguments = '-T4 -n'  # Connect scan
    for intf in local_interfaces:
        ifname, network, prefix = intf['ifname'], intf['network'], intf['prefix']
        print "Scanning on interface %s network %s/%s" % (ifname, network, prefix)
        hosts = '%s/%s' % (network, prefix)
        ports = '%s' % (CAMERA_PORT)
        nm.scan(hosts, ports, arguments)
        for host in nm.all_hosts():
            if nm[host].has_tcp(CAMERA_PORT) and \
                    nm[host]['tcp'][CAMERA_PORT]['state'] == 'open':
                cameras.append(host)

    for camera in cameras:
        url = 'http://%s:%s/' % (camera, CAMERA_PORT)
        print 'Camera:', url
        response = requests.get(url)
        if response.status_code == 200:
            print response.headers['server']
            print
        else:
            print 'Error:', response.status_code




