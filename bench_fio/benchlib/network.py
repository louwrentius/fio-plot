#!/usr/bin/env python3
import socket
import sys
def remote_checks(settings):
    if settings["remote"] and settings["remote_checks"]:
        print(f"\nWe are checking remote hosts for active fio server at TCP port 8765...")
        print(f"\n")
        failed_list = []
        with open(settings["remote"], 'r') as file:
            hosts = file.read().splitlines() 
            for host in hosts:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(int(settings["remote_timeout"])) #Second Timeout
                testresult = sock.connect_ex((host,8765))
                sock.close()
                if testresult != 0:
                    failed_list.append(host)
        if failed_list:
            for host in failed_list:
                print(f"Host {host} is unreachable on TCP port 8765")
            print(f"\n")
            sys.exit(1)