#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# gNrg(at)tuta.io
#

import os
import optparse
from contextlib import closing
from selenium.webdriver import Firefox # pip install selenium
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup # easy_install beautifulsoup4
from getpass import getpass

header = '''+---------------------------------------------------+
|                                                   |
|                   CDE-30364.py                    |
|                     by  gNrg                      |
|                                                   |
+---------------------------------------------------+\n'''
version = "%prog V0.1"
usage   = "usage: %prog [-u  <user>][-p  <pass>][-i  <ip>][-k  <file>][-o <file>]"
desc    = """A simple python script to get active IPs on LAN managed 
with a Hitron CDE-30364 router model. This script has been 
optimizated to firmware PSPU-Boot 1.0.16.22-H2.8.3 therefore 
using a different firmware version can cause errors."""

hosts   = []
types   = []
ips     = []
macs    = []
ifaces  = []
clients = []
known_macs = []

def print_header():
    os.system("clear")
    print header
def get_known_macs(kmfile):
    known_macs = []
    try:
        file = open(kmfile, 'r')
        print "\nOpen file:\t\t\t[[ OK ]]"
        file_content = file.read()
        for line in file_content.split("\n"):
            a, b = line.split(" ")
            known_macs.append([a, b])
        print "Getting file information:\t[[ OK ]]"
        file.close()
        print "Close file:\t\t\t[[ OK ]]"
        return known_macs
    except IOError: 
        print("Open/Read file:  [[ ERROR ]]")
        print("\tCheck if the path is correct.")
        print("\tCheck if do you have permissions for read the file.")
        print("\tThen, try again.")
        raw_input("Press enter to continue...")
        return []

class Client():
    def __init__(self, hostname = '', ip = '', mac = '', tp = '', iface = ''):
        self.hostname = hostname
        self.ip = ip
        self.mac = mac
        self.type = tp
        self.iface = iface
    def get_hostname(self): return self.hostname
    def get_ip(self): return self.ip
    def get_mac(self): return self.mac
    def get_type(self): return self.type
    def get_iface(self): return self.iface
    def set_hostname(self, hostname): self.hostname = hostname
    def set_ip(self, ip): self.ip = ip
    def set_mac(self, mac): self.mac = mac
    def set_type(self, tp): self.type = tp
    def set_iface(self, iface): self.iface = iface
    def display(self):
        print "\nHostname:\t" + self.hostname
        print "IP:\t\t" + self.ip
        print "MAC:\t\t" + self.mac
        print "Type:\t\t" + self.type
        print "Interface:\t" + self.iface + '\n'
    def to_text(self):
        s = "\nHostname:\t" + self.hostname + '\n'
        s += "IP:\t\t" + self.ip + '\n'
        s += "MAC:\t\t" + self.mac + '\n'
        s += "Type:\t\t" + self.type + '\n'
        s += "Interface:\t" + self.iface + '\n'
        return s

if __name__ == '__main__':
    # Configure script options
    parser = optparse.OptionParser(description = desc, version = version, usage = usage)
    parser.add_option("-u", "--user", dest="user",
                        default="admin", type="string", metavar='<USERNAME>', 
                        help="Setup user value")
    parser.add_option("-p", "--password", dest="password",
                        default="admin", type="string", metavar='<PASSWORD>', 
                        help="Setup password value")
    parser.add_option("-i", "--ip", dest="ip",
                        default="192.168.1.1", type="string", metavar='<NNN.NNN.NNN.NNN>', 
                        help="Setup router IP value")
    parser.add_option("-k", "--known-macs", dest="kmfile",
                        default="", type="string", metavar='<FILE>', 
                        help="Use that file to compare the found MACs and identify known/unknown clients")
    parser.add_option("-o", "--output", dest="output",
                        default="", type="string", metavar='<FILE>', 
                        help="Save output in text file")
    (opts, args) = parser.parse_args()

    print_header()
    login_url   = "http://" + opts.ip + "/login.asp"
    target_url  = "http://" + opts.ip + "/admin/feat-lan-ip.asp"

    # Get KnownMACs file content
    if opts.kmfile:
        known_macs = get_known_macs(opts.kmfile) # MAC [0] - Name [1]

    print_header()
    print "\nGetting information from the router..."
    # Use firefox to get page with javascript generated content
    with closing(Firefox()) as browser:
        browser.get(login_url)
        try:
            WebDriverWait(browser, timeout=10).until(
                lambda x: x.find_element_by_id('logincontent'))
            userbox = browser.find_element_by_id('username')
            passwordbox = browser.find_element_by_id('password')
            userbox.send_keys(opts.user)
            passwordbox.send_keys(opts.password)
            button = browser.find_element_by_class_name('login_button')
            button.click()
            print "Login:\t\t[[ OK ]]\n"
        except: 
            print "Login:\t\t[[ ERROR ]]\n"
            exit(-1)
        browser.get(target_url)
        try:
            WebDriverWait(browser, timeout=10).until(
                lambda x: x.find_element_by_id('connected_computers'))
            page_source = browser.page_source
        except: 
            print "Getting info:\t\t[[ ERROR ]]\n"
            exit(-1)
    print "Getting info:\t\t[[ OK ]]\n"

    soup = BeautifulSoup(page_source, 'lxml')
    html_hostnames = soup.find_all(attrs={"class": "lan_ip_table_mid"})
    for host in html_hostnames[1:-1]: hosts.append(host.get_text())
    html_ips = soup.find_all(attrs={"class": "lan_ip_table_mid2"})
    for ip in html_ips[2:]: ips.append(ip.get_text())
    html_macs = soup.find_all(attrs={"class": "lan_ip_table_big"})
    for mac in html_macs[2:-1]: macs.append(mac.get_text())
    html_ifaces = soup.find_all(attrs={"class": "lan_ip_table_small"})
    for iface in html_ifaces[2:]: ifaces.append(iface.get_text())

    for x in range(0, len(hosts)):
        if x % 2 != 0: types.append(hosts[x])
    for t in types: hosts.remove(t)

    for x in range(0, len(hosts)):
        clients.append(Client(hosts[x], ips[x], macs[x], types[x], ifaces[x]))
    
    for c in clients: c.display()

    if opts.output:
        text = ''
        for c in clients: text += c.to_text()
        # create/open and write file
        #print text
