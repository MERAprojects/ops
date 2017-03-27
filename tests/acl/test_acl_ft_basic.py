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

Tests:
TC_ACL_1    Verify that ping from host1 to host2 is absent when ACL is configured as deny for it
    Steps:
        1. Actions: Create 3 hosts and a switch, connect hosts to switch; configure IP addresses on ports;
            Result: there are no any errors;
        2. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: there is not more than 1 package lost in every iteration;
        3. Actions: Create access-list TC_ACL_1, set a rule which denies any traffic from Host1 to Host2;
            Result: there are no any errors;
        4. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: there is not more than 1 package lost when Host1 pings Host3 and Host2 pings Host3
                    all packages are lost when Host1 pings Host2
TC_ACL_2    Verify that ping from host1 to host2 is presented when ACL is configured as permit for it
    Steps:
        1. Actions: Create 3 hosts and a switch, connect hosts to switch; configure IP addresses on ports;
            Result: there are no any errors;
        2. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: there is not more than 1 package lost in every iteration;
        3. Actions: Create access-list TC_ACL_2, set a rule which permits any traffic from Host1 to Host2;
            Result: there are no any errors;
        4. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: there is not more than 1 package lost in every iteration
TC_ACL_3    Try to create 1000 access lists. Expected: succesfully
    Steps:
        1. Actions: Create 3 hosts and a switch, connect hosts to switch; configure IP addresses on ports;
            Result: there are no any errors;
        2. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: there is not more than 1 package lost in every iteration;
        3. Actions: Create access-list TC_ACL_3, create 1000 rules which deny any traffic from any IP addresses
            to any interfaces;
            Result: there are no any errors, 1000 rules are created without any errors;
        4. Actions: Host1 pings Host2, Host1 pings Host3, Host2 pings Host3;
            Result: all packages are lost in every iteration

'''

import re
import pytest
from opstestfw import *
from opstestfw.switch.CLI import *
from opstestfw.switch.CLI.showRun import *
from opstestfw.switch.OVS import *
import opstestfw.testEnviron
import opstestfw.Device
from opsvsiutils.vtyshutils import *

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

#the function expects successfull command execution
def sendCommand(dut,cmd):
    if (enterConfigShell(dut) is False):
        enterConfigShell(dut)
    retStruct = dut.DeviceInteract(command=cmd)
    buffer=retStruct.get("buffer")
    assert retStruct.get("returnCode") == 0,\
        "There are problems with command execution. Check output below:\n" + buffer
    # assert not("% Unable" in buffer),\
    #     "Command is not executed because :\n"+buffer
    LogOutput("info","Output command: \"" +cmd+"\" is:\n "+buffer)
    return True

# syntax
# access-list ip <acl-name>
def createAccessList(**kwargs):
    device=kwargs.get("device")
    accessListName=kwargs.get("name")
    cmd="access-list ip "+accessListName
    resultBoolean=sendCommand(device, cmd)
    runningConfig = device.DeviceInteract(command="do sh run").get("buffer")
    if not (cmd in runningConfig):
        resultBoolean = False
    return resultBoolean

# syntax
# [<sequence-number>]
#          {permit|deny}
#          {any|ah|gre|esp|icmp|igmp|pim|<ip-protocol-num>}
#          {any|<src-ip-address>[/{<prefix-length>|<subnet-mask>}]}
#          {any|<dst-ip-address>[/{<prefix-length>|<subnet-mask>}]}
#          [count] [log]
#     [no] [<sequence-number>]
#          {permit|deny}
#          {sctp|tcp|udp}
#          {any|<src-ip-address>[/{<prefix-length>|<subnet-mask>}]}
#          [{eq|gt|lt|neq} <port>|range <min-port> <max-port>]
#          {any|<dst-ip-address>[/{<prefix-length>|<subnet-mask>}]}
#          [{eq|gt|lt|neq} <port>|range <min-port> <max-port>]
#          [count] [log]
def createRuleAccessList(**kwargs):
# TO DO: add checking you are in access list configuration mode (switch(config-acl)# )
    device=kwargs.get("device")                    # deviceObj
    sequence=str(kwargs.get("sequence",""))        # (<1-4294967295>,None)
    type=kwargs.get("type","permit")               # (deny | permit)
    protocol=kwargs.get("protocol","any")          # (any | ah | gre | esp | icmp | igmp |  pim | sctp | tcp | udp | <0-255>)
    source=kwargs.get("source","any")              # (any | A.B.C.D | A.B.C.D/M | A.B.C.D/W.X.Y.Z)
    destination=kwargs.get("destination","any")    # (any | A.B.C.D | A.B.C.D/M | A.B.C.D/W.X.Y.Z)
    statistic=kwargs.get("statistic","")           # {log | count}

    # with destination/source ports
    if (protocol==("sctp"or"tcp"or"udp")):
        sourcePort=kwargs.get("sourcePort","")              # {eq|gt|lt|neq} <port>|range <min-port> <max-port>
        destinationPort=kwargs.get("destinationPort","")    #{eq|gt|lt|neq} <port>|range <min-port> <max-port>
        cmd=sequence+space+type+space+protocol+space+\
            source+space+sourcePort+space+\
            destination+space+destinationPort+space+\
            statistic
    else:
        cmd=sequence+space+type+space+protocol+\
            space+source+space+destination+space+statistic
    resultBoolean=sendCommand(device, cmd)
#TO DO: Module opstestfw.switch.CLI.showRun shoud be used to check running config,
# but before need to extend it for ConfigVtyShell mode
    runningConfig = device.DeviceInteract(command="do sh run").get("buffer")
    if not (cmd in runningConfig):
        resultBoolean = False
    return resultBoolean

#it is not implemented
def deleteAccessList(**kwargs):
#TO DO write the method which deletes access lists
    pass

#it is not implemented
def deleteRulesAccessList(**kwargs):
#TO DO write the method which deletes access list rules
    pass

class Test_ACL_configuration:
    def setup(self):
        # Test object will parse command line and formulate the env
        self.testObj = testEnviron(topoDict=topoDict,defSwitchContext="vtyShell")
        # Get ping topology object
        self.pingTopoObj = self.testObj.topoObjGet()

    def teardown(self):
        self.pingTopoObj.terminate_nodes()

    # TC_ACL_1    Verify that ping from host1 to host2 is absent when ACL is configured as deny for it
    def test_acl_1(self):
        accessListName="TC_ACL_1"

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
        assert createAccessList(device=dut01Obj, name=accessListName), "Failed to create " + accessListName
        assert (createRuleAccessList(device=dut01Obj, type="deny",
                                     source=ipHost1+slash+maskHost1, destination=ipHost2+slash+maskHost2)), \
            "It is impossible to create rule for access-list"

        stepFrame('4', "Check ACL configuration")
        #check access-list blocks ping h1=>h2, but does not block ping h1=>h3 and h2=h3
        ping1 = verifyPing(wrkston01Obj, destIPAddress=ipHost2)
        ping2 = verifyPing(wrkston01Obj, destIPAddress=ipHost3)
        ping3 = verifyPing(wrkston02Obj, destIPAddress=ipHost3)
        assert (ping1 is False) and ((ping2 and ping3) is True),\
            "Test case is failed"

    # TC_ACL_2    Verify that ping from host1 to host2 is presented when ACL is configured as permit for it
    def test_acl_2(self):
        accessListName = "TC_ACL_2"

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
        assert createAccessList(device=dut01Obj, name=accessListName), "Failed to create " + accessListName
        assert (createRuleAccessList(device=dut01Obj, source=ipHost1+slash+maskHost1, destination=ipHost2+slash+maskHost2)), \
            "It is impossible to create rule for access-list"

        stepFrame('4', "Check ACL configuration")
        #check access-list blocks ping h1=>h2, but does not block ping h1=>h3 and h2=h3
        ping1 = verifyPing(wrkston01Obj, destIPAddress=ipHost2)
        ping2 = verifyPing(wrkston01Obj, destIPAddress=ipHost3)
        ping3 = verifyPing(wrkston02Obj, destIPAddress=ipHost3)
        assert (ping1 and ping2 and ping3), "Test case is failed"

    #TC_ACL_3   Try to create 1000 access lists. Expected: succesfully
    def test_acl_3(self):
        maxQuantityAcls=1000
        accessListName="TC_ACL_3"

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
        assert createAccessList(device=dut01Obj,name=accessListName), "Failed to create "+accessListName
        for i in range(1, maxQuantityAcls):
            assert (createRuleAccessList(device=dut01Obj,type="deny",sequence=i)),\
                "It is impossible to create more than "+str(i-1)+" access-lists"

        stepFrame('4', "Check ACL configuration")
        #check access-list blocks ping h1=>h2, but does not block ping h1=>h3 and h2=h3
        ping1 = verifyPing(wrkston01Obj, destIPAddress=ipHost2)
        ping2 = verifyPing(wrkston01Obj, destIPAddress=ipHost3)
        ping3 = verifyPing(wrkston02Obj, destIPAddress=ipHost3)
        assert not (ping1 and ping2 and ping3), "Test case is failed. Ping shouldn`t work. " \
                                                "Because there are set deny access lists for any IP addresses" \
                                                "to any interfaces"
