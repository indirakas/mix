#!/usr/bin/python
from jinja2 import Environment, Template, FileSystemLoader
import codecs
import re
#creates a Cisco switch object
class SwitchData(object):
        def __init__(self):
                self.hostname = ""
                self.vlan = 0
                self.port = 0
                self.ipaddress = ""
#creates a Brocade switch object              
class BrocadeSwitchData(object):
        def __init__(self):
                self.rbridge = 0
                self.rbridge_start = 0
                self.vlan_userport={}
                self.vlan_uplinkport={}
                self.vlans = set()
                self.leng = 0
                self.sum1={}
                self.sum2={}
                self.sum2_list=[]
                self.hostname = []
                self.ipaddress = ""
                self.mgmt_ip = []
                self.inter = 0
                self.model = ""
                self.version = ""
#class to throw an exception with printed "error" message , if "condition" does not match
def exception(x,condition,error):
        try:
                if condition:
                        return x
        except TypeError,ValueError:
                print "Not a valid name"
                
        else:
                raise Exception(error)

#class to create a file, called $hostname.cfg in the same directory
def write(hostname,output):
        try:
                with codecs.open("%s.cfg"% hostname, "wb","utf-8") as f:
                        f.write(output)
                        f.close()
        except IOError:
                print "Can\'t find file or read data"
        else:
                print "Written content to the file %s successfully" % hostname
        return output
#class to identify number of ports on a switch, given the provided version number
def check_model(model,inter):
        if model == "6740" or "6740T":
                inter = 52
        else:
                inter = int(model[-2:])
                model = model[:-3]
        return model,inter
#class to create a tuple of non-duplicated vlans
def count_vlans(sumx,vlans):
        
        for rb in sumx.keys():
                for vlan in sumx[rb]:
                        vlans.add(vlan)
        return vlans
#class to create a list of ..
def sum2_list(s,lst):
        tmp=[]
        for keys,(value1,value2) in s.values()[0].items():
                print s,lst
                tmp.append(keys)
                tmp1=[value1,value2]
                lst=[tmp,tmp1]
        return lst
#main class
def main():
        ENV = Environment(loader=FileSystemLoader('.'))
        ENV.globals.update(zip=zip)
        #only two vendors are covered - brocade and cisco
        vendor_list=["brocade","cisco"]
        #only the following digits are allowed in the name: 0-9, a-z and dash
        regex = re.compile('[0-9,a-z,-]+$')
        vendor=raw_input("Enter a switch vendor: ")
        vendor=exception(vendor,vendor in vendor_list,"Not a valid vendor")
        if vendor == "cisco":
                #creates a Cisco switch object
                cisco_switch=SwitchData()
                #loads a Jinja2 template
                template = ENV.get_template("base-config.j2")
                #only the following vlans are allowed to be provided by the user
                vlan_list=[10,20,30,40,50]
                cisco_switch.hostname=raw_input("Enter a switch hostname: ")
                cisco_switch.hostname=exception(cisco_switch.hostname,\
                                                regex.match(cisco_switch.hostname),\
                                                "Hostname contains invalid characters")
                print cisco_switch.hostname
                #requests to provide a port on a distribution switch this switch is connected to
                cisco_switch.port=int(raw_input("Enter the port on management switch: "))
                cisco_switch.port=exception(cisco_switch.port,\
                                            cisco_switch.port < 49 and cisco_switch.port > 0,\
                                            "Port must be up to 48")
                print cisco_switch.port
                #only vlans in the vlan_list are allowed
                cisco_switch.vlan=int(raw_input("Enter an end-user vlan: "))
                cisco_switch.vlan=exception(cisco_switch.vlan,\
                                            cisco_switch.vlan in vlan_list,\
                                            "Vlan must be private mgmt")
                print cisco_switch.vlan
                #switch IP address must be valid in 172.16.16.0/20 range
                cisco_switch.ipaddress=raw_input("Enter switch ip address: ")
                cisco_switch.ipaddress=exception(cisco_switch.ipaddress,\
                                                 cisco_switch.ipaddress.startswith("172.16.") and int(cisco_switch.ipaddress.split(".")[3])<=254 and int(cisco_switch.ipaddress.split(".")[2]) in range (16,32),\
                                                 "Please select address from 172.16.16.0/20 subnet")
                #parameters are gathered in total and passed to the template
                total = {"hostname":cisco_switch.hostname,\
                         "port":cisco_switch.port,\
                         "vlan":cisco_switch.vlan,\
                         "ipaddress":cisco_switch.ipaddress}
                #the template outcome is written to the file hostname.cfg
                output=write(cisco_switch.hostname,template.render(data=total))
                
        elif vendor == "brocade":
                #creates a Brocade switch object
                vdx_switch=BrocadeSwitchData()
                #loads a Jinja2 template
                template = ENV.get_template("base-config-brocade.j2")
                #only the following versions are allowed (this list will be updated)
                version_list=["4.1.3c","5.0.2a"]
                #only the following vlans are allowed
                ivlan_list=[1,2,3]
                pvlan_list=[11,22,33]
                rvlan_list=[111,222,333]
                #gathers information of the switch version
                vdx_switch.version=raw_input("Enter the switch version: ")
                vdx_switch.version=exception(vdx_switch.version,\
                                             vdx_switch.version in version_list or vdx_switch.version.strip("nos") in version_list,\
                                             "Version is not supported by Brocade VDX")
                #gathers information of switch model
                vdx_switch.model=raw_input("Enter the switch model: ")
                vdx_switch.model=exception(vdx_switch.model,\
                                           vdx_switch.model.startswith("67"),\
                                           "VDX switch model does not exist")
                #gets port number ("inter") and model name
                vdx_switch.model,vdx_switch.inter=check_model(vdx_switch.model,vdx_switch.inter)
                #gathers rbridge-id for the first switch in the logical chassis
                vdx_switch.rbridge_start=int(raw_input("Enter starting rbridge number: "))
                vdx_switch.rbridge_start=exception(vdx_switch.rbridge_start,\
                                             vdx_switch.rbridge_start<239,\
                                             "Rbridge value must be between 1 and 239")
                #gathers number of rbridges present in the logical chassis
                vdx_switch.rbridge=int(raw_input("Enter number of rbridges in a logical chassis: "))
                vdx_switch.rbridge=exception(vdx_switch.rbridge,\
                                             vdx_switch.rbridge<239,\
                                             "Rbridge value must be between 1 and 239")
                #gathers an IP address of the logical chassis
                vdx_switch.ipaddress=raw_input("Enter VCS IP address: ")
                vdx_switch.ipaddress=exception(vdx_switch.ipaddress,\
                                               vdx_switch.ipaddress.startswith("172.16.") and int(vdx_switch.ipaddress.split(".")[3])<=254 and int(vdx_switch.ipaddress.split(".")[2]) in range (16,32),\
                                               "Address is either not in a range 172.16.16.0/20 or one of the octets is invalid") 
                #since each pair of distribution switches act in a HA mode and port-channels are created one per pair...
                #...the following variable "d" is created
                d=0
                for rb in range(0,vdx_switch.rbridge):
                        #if rbridge number is even - "d" equals to it, if it is odd - "d" equals to rb-1
                        if rb % 2 ==0:
                                d=rb
                        else:
                                d=rb-1
                        
                        vdx_switch.sum1[(rb+vdx_switch.rbridge_start)]={}
                        vdx_switch.sum2[(rb+vdx_switch.rbridge_start)]={}
                        vdx_switch.hostname.append(raw_input("Enter %d switch hostname (rbridge %d): " % ((rb+1),(rb+vdx_switch.rbridge_start))))
                        vdx_switch.hostname[rb]=exception(vdx_switch.hostname[rb],\
                                                regex.match(vdx_switch.hostname[rb]),
                                                "Hostname contains invalid characters")
                        vdx_switch.mgmt_ip.append(raw_input("Enter %d switch ip address (rbridge %d): " % ((rb+1),(rb+vdx_switch.rbridge_start))))
                        vdx_switch.mgmt_ip[rb]=exception(vdx_switch.mgmt_ip[rb],\
                                                         vdx_switch.mgmt_ip[rb].startswith("172.16.") and int(vdx_switch.mgmt_ip[rb].split(".")[3]) <= 254 and int(vdx_switch.mgmt_ip[rb].split(".")[2]) in range (16,32),\
                                                         "Address is either not in a range 172.16.16.0/20 or one of the octets is invalid")
                        
                        if d==rb:
                                while True:
                                        vlan=int(raw_input("Enter vlan for rbridge %d and %d: (or type 0 stop)" % (d+vdx_switch.rbridge_start,d+vdx_switch.rbridge_start+1)))
                                        if vlan!=0:
                                                userport_begin=int(raw_input("Start port to end-hosts: "))
                                                userport_end=int(raw_input("End port to end-hosts: "))
                                                userport_begin=exception(userport_begin,userport_begin and  userport_end <= vdx_switch.inter and userport_begin and  userport_end >= 1 and userport_begin <= userport_end,"Pick a correct number")
                                                userport_end=exception(userport_end,userport_begin and  userport_end <= vdx_switch.inter and userport_begin and  userport_end >= 1 and userport_begin <= userport_end,"Pick a correct number")

                                                vlan=exception(vlan,vlan > 1 and vlan <= 4090,"Vlan is incorrect")
                                                vdx_switch.sum1[d+vdx_switch.rbridge_start][vlan]=[userport_begin,userport_end]
                                                
                                                uplink_begin=int(raw_input("Start port to uplink switch or router: "))
                                                uplink_end=int(raw_input("End port to uplink switch or router: "))
                                                vdx_switch.sum2[d+vdx_switch.rbridge_start][vlan]=[(exception(uplink_begin,\
                                                                                  uplink_begin and uplink_end <= vdx_switch.inter and uplink_begin and uplink_end >= 1 and uplink_begin <= uplink_end,\
                                                                                  "Pick a correct number")),\
                                                                              (exception(uplink_end,\
                                                                                uplink_begin and uplink_end <= vdx_switch.inter and uplink_begin and uplink_end >= 1 and uplink_begin <= uplink_end,\
                                                                                "Pick a correct number"))]
                                                continue
                                        else:
                                                break
                        else:
                               
                                vdx_switch.sum1[rb+vdx_switch.rbridge_start]=vdx_switch.sum1[d+vdx_switch.rbridge_start]
                                vdx_switch.sum2[rb+vdx_switch.rbridge_start]=vdx_switch.sum2[d+vdx_switch.rbridge_start]
                
                vdx_switch.vlans=count_vlans(vdx_switch.sum1,vdx_switch.vlans)
                
                vdx_switch.sum2_list=sum2_list(vdx_switch.sum2,vdx_switch.sum2_list)
                
                total= {"version":vdx_switch.version,\
                        "model":vdx_switch.model,\
                        "inter":vdx_switch.inter,\
                        "rbridge_start":vdx_switch.rbridge_start,\
                        "rbridge":vdx_switch.rbridge,\
                        "hostname":vdx_switch.hostname,\
                        "ipaddress":vdx_switch.ipaddress,\
                        "mgmt_ip":vdx_switch.mgmt_ip,\
                        "sum2_list":vdx_switch.sum2_list,\
                        "vlans":vdx_switch.vlans,\
                        "sum1":vdx_switch.sum1}
                        
                output=write(vdx_switch.hostname[0],template.render(data=total))

        else:
                raise Exception("Invalid vendor")
if __name__ == "__main__":
        main()
