# 2017 MeraNN

'''
Basic configuration:
int eth1 is 192.168.110.1/24
int eth2 is 192.168.120.1/24
int eth3 is 192.168.130.1/24

Host 1 Configuration
IP ADDR is 192.168.110.2/24
 Host 2 Configuration
IP ADDR is 192.168.120.2/24
 Host 3 Configuration
IP ADDR is 192.168.130.2/24

 +---------+             +----------+            +---------+
 |         |             |          |            |         |
 |         |             |          |            |         |
 | Host1   .2--------- .1  Switch1 .1----------.2   Host2  |
 |         |192.168.110. |          |192.168.120.|         |
 |         |             |          |            |         |
 +---------+             +---.1-----+            +---------+
                              |
                              |192.168.130.
                              |
                         +---.2----+
                         |         |
                         |         |
                         |  Host3  |
                         |         |
                         |         |
                         +---------+

TC_ACL_1 basic config



'''


import pytest
from opstestfw import *
from opstestfw.switch.CLI import *
from opstestfw.switch.OVS import *
import opstestfw.testEnviron
import opstestfw.Device
import re
from opsvsiutils.vtyshutils import *


debug=True

#variables:
slash="/"
space=" "
dot="."
#IP address setings
#hosts
ipHost1 = "192.168.110.2"
maskHost1 = "255.255.255.0"
gatewayHost1 = "192.168.110.1"
broadcastHost1 = "192.168.110.255"

ipHost2 = "192.168.120.2"
maskHost2 = "255.255.255.0"
gatewayHost2 = "192.168.120.1"
broadcasHost2 = "192.168.120.255"

ipHost3 = "192.168.130.2"
maskHost3 = "255.255.255.0"
gatewayHost3 = "192.168.130.1"
broadcastHost3 = "192.168.130.255"

defaultGatewayNetwork = "0.0.0.0"
defaultGatewayMask = "0.0.0.0"

#switch
ipLink1Switch1 = "192.168.110.1"
maskLink1Switch1 = "24"
ipLink2Switch1 = "192.168.120.1"
maskLink2Switch1 = "24"
ipLink3Switch1 = "192.168.130.1"
maskLink3Switch1 = "24"

#links
lnk01="lnk01"
lnk02="lnk02"
lnk03="lnk03"

topoDict = {"topoExecution": 1000,
            "topoTarget": "dut01",
            "topoDevices": "dut01 wrkston01 wrkston02 wrkston03",
            "topoLinks": "lnk01:wrkston01:dut01,\
                          lnk02:wrkston02:dut01,\
                          lnk03:wrkston03:dut01",
            "topoFilters": "dut01:system-category:switch,\
                            wrkston01:system-category:workstation,\
                            wrkston02:system-category:workstation,\
                            wrkston03:system-category:workstation"}


def configure(**kwargs):
    LogOutput('info', "starting configure")
    switch1 = kwargs.get('switch1', None)
    host1 = kwargs.get('host1', None)
    host2 = kwargs.get('host2', None)
    host3 = kwargs.get('host3', None)
# configure host1
    LogOutput('info', "Configuring host1 with IPv4 address")
    retStruct = host1.NetworkConfig(ipAddr = ipHost1,
                                    netMask = maskHost1,
                                    broadcast = broadcastHost1,
                                    interface=host1.linkPortMapping[lnk01],
                                    config=True)
    if retStruct.returnCode() != 0:
        assert "Failed to configure IPv4 address on Host1"
    LogOutput('info', "Configuring default gateway on host1")
    retStruct = host1.IPRoutesConfig(config=True,
                                     destNetwork=defaultGatewayNetwork,
                                     netMask=defaultGatewayMask,
                                     interface=host1.linkPortMapping[lnk01],
                                     gateway=gatewayHost1)

    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure default gateway on host1"

    LogOutput('info', "Configuring host2 with IPv4 address")
    retStruct = host2.NetworkConfig(ipAddr = ipHost2,
                                    netMask = maskHost2,
                                    broadcast = broadcasHost2,
                                    interface=host2.linkPortMapping[lnk02],
                                    config=True)
    if retStruct.returnCode() != 0:
        assert "Failed to configure IPv4 address on Host2"
    LogOutput('info', "Configuring default gateway on host2")
    retStruct = host2.IPRoutesConfig(config=True,
                                     destNetwork=defaultGatewayNetwork,
                                     gateway=gatewayHost2,
                                     netMask=defaultGatewayMask,
                                     interface=host2.linkPortMapping[lnk02]
                                     )
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure default gateway on host2"

    LogOutput('info', "Configuring host3 with IPv4 address")
    retStruct = host3.NetworkConfig(ipAddr = ipHost3,
                                    netMask = maskHost3,
                                    broadcast = broadcastHost3,
                                    interface=host3.linkPortMapping[lnk03],
                                    config=True)
    if retStruct.returnCode() != 0:
        assert "Failed to configure IPv4 address on Host3"
    LogOutput('info', "Configuring default gateway on host3")
    retStruct = host3.IPRoutesConfig(config=True,
                                     destNetwork=defaultGatewayNetwork,
                                     gateway=gatewayHost3,
                                     netMask=defaultGatewayMask,
                                     interface=host3.linkPortMapping[lnk03]
                                     )
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure default gateway on host3"

    # Enabling interface 1 SW1
    LogOutput('info', "Enabling interface1 on SW1")
    retStruct = InterfaceEnable(deviceObj=switch1, enable=True,
                                interface=switch1.linkPortMapping[lnk01])
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Unable to enable interface1 on SW1"

    # Enabling interface 2 SW1
    LogOutput('info', "Enabling interface2 on SW1")
    retStruct = InterfaceEnable(deviceObj=switch1, enable=True,
                                interface=switch1.linkPortMapping[lnk02])
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Unable to enable interface2 on SW1"

    # Enabling interface 3 SW1
    LogOutput('info', "Enabling interface3 on SW1", datastamp=True)
    retStruct = InterfaceEnable(deviceObj=switch1, enable=True,
                                interface=switch1.linkPortMapping[lnk03])
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Unable to enable interface3 on SW1"

    # Entering interface for link 1 SW1, giving an IPv4 address
    LogOutput('info', "Configuring IPv4 address on link 1 SW1")
    retStruct = InterfaceIpConfig(deviceObj=switch1,
                                  interface=switch1.linkPortMapping[lnk01],
                                  addr=ipLink1Switch1, mask=maskLink1Switch1, config=True)
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure an IPv4 address for SW1 (lnk to host1)"

    LogOutput('info', "Configuring IPv4 address on link 2 SW1")
    retStruct = InterfaceIpConfig(deviceObj=switch1,
                                  interface=switch1.linkPortMapping[lnk02],
                                  addr=ipLink2Switch1, mask=maskLink2Switch1, config=True)
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure an IPv4 address for SW1 (lnk to host2)"

    LogOutput('info', "Configuring IPv4 address on link 3 SW1")
    retStruct = InterfaceIpConfig(deviceObj=switch1,
                                  interface=switch1.linkPortMapping[lnk03],
                                  addr=ipLink3Switch1, mask=maskLink3Switch1, config=True)
    retCode = retStruct.returnCode()
    if retCode != 0:
        assert "Failed to configure an IPv4 address for SW1 (lnk to host3)"

def stepFrame(step,header):
    LogOutput('info', "############################################")
    LogOutput('info', "Step " + step + dot + space + header)
    LogOutput('info', "############################################")

def verifyPing(clientSource, destIPAddress):
    host = "Host" + clientSource.device.split('wrkston0')[-1]
    LogOutput('info',host  + " tryes to ping " + destIPAddress)
    pingResult = clientSource.Ping(ipAddr=destIPAddress)
    if pingResult.returnCode() != 0:
        LogOutput('error', "Ping failed...\n")
        return False
    else:
        LogOutput('info', "Ping to " + destIPAddress + "... \n")
        packet_loss = pingResult.valueGet(key='packet_loss')
    #10% is value to resolve ARPs
    if packet_loss > 10:
        LogOutput('error', "Packet Loss > 10%, lost " + str(packet_loss))
        return False
    else:
        LogOutput('info', "Success is more than 90%...\n")
    return True

def enterConfigShell(dut):
    retStruct = dut.VtyshShell(enter=True)
    retCode = retStruct.returnCode()
    assert retCode == 0, "Failed to enter vtysh prompt"

    retStruct = dut.ConfigVtyShell(enter=True)
    retCode = retStruct.returnCode()
    assert retCode == 0, "Failed to enter config terminal"
    return True

def sendCommand(dut,cmd):
    if (enterConfigShell(dut) is False):
        LogOutput("error","You are not in configuration mode.\n Failed execute: " + cmd)
        return False
    else:
        buffer = dut.DeviceInteract(command=cmd).get("buffer")
        LogOutput("info","Output command: \"" +cmd+"\" is:\n "+buffer)
        return True



class Test_ACL_configuration:
    def setup_class(self):
        # Test object will parse command line and formulate the env
        self.testObj = testEnviron(topoDict=topoDict,defSwitchContext="vtyShell")
        # Get ping topology object
        self.pingTopoObj = self.testObj.topoObjGet()

    def teardown_class(self):
        self.pingTopoObj.terminate_nodes()

    def test_access_list_permit_in(self):
        # Initial configuration
        print Hosts
        stepFrame('1', "Configure ip-addresses")
        dut01Obj = self.pingTopoObj.deviceObjGet(device="dut01")
        wrkston01Obj = self.pingTopoObj.deviceObjGet(device="wrkston01")
        wrkston02Obj = self.pingTopoObj.deviceObjGet(device="wrkston02")
        wrkston03Obj = self.pingTopoObj.deviceObjGet(device="wrkston03")
        configure(switch1=dut01Obj, host1=wrkston01Obj, host2=wrkston02Obj, host3=wrkston03Obj)

        stepFrame('2', "Check configuration before TC")
        # Check initial configuration (ping h1=>h2, h1=>h3, h2=>h3)
        ping1 = verifyPing(wrkston01Obj,destIPAddress=ipHost2)
        ping2 = verifyPing(wrkston01Obj,destIPAddress=ipHost3)
        ping3 = verifyPing(wrkston02Obj,destIPAddress=ipHost3)
        assert (ping1 and ping2 and ping3), "Test configuration is not prepared"

        stepFrame('3', "ACL configuration")
        #apply access-list settings
        assert enterConfigShell(dut01Obj), "Failed to go in Config Shell"
        sendCommand (dut01Obj,"access-list ip TC_ACL_1")
        sendCommand (dut01Obj,"deny any "+ipHost1+slash+maskHost1+space+
                     ipHost2+slash+maskHost2)

        stepFrame('4', "Check ACL configuration")
        #check access-list blocks ping h1=>h2, but does not block ping h1=>h3 and h2=h3
        ping1 = verifyPing(wrkston01Obj, destIPAddress=ipHost2)
        ping2 = verifyPing(wrkston01Obj, destIPAddress=ipHost3)
        ping3 = verifyPing(wrkston02Obj, destIPAddress=ipHost3)
        assert (ping1 is False) and ((ping2 and ping3) is True),\
            "Test configuration is not prepared"

