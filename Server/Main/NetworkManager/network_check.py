from socket import getaddrinfo, gethostname
from platform import system as operating_system
from sys import argv

dev = False

if argv[1:]:
    dev = True

def ip_checker():
    if dev:
        return {
            "host": 'localhost',
            "status": True
        }

    else:
        if operating_system() == "Linux":
            from netifaces import interfaces, ifaddresses
            interf = interfaces()
            ips = ifaddresses(interf[2])
            if len(ips) > 1:
                ip = ips[2][0]['addr']
            else:
                ip = '127.0.0.1'
            
        else:
            system_ip_list = getaddrinfo(gethostname(), None, 0, 1, 0)
            ip =  system_ip_list[-1][4][0]

        if ip == '127.0.0.1':
            return {
                "host": 'localhost',
                "status": False
            }
        
        else:
            return {
                "host": ip,
                "status": True
            }