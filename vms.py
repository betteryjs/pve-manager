# import json
import time

import paramiko
from proxmoxer import ProxmoxAPI
from config import Config
from vm import VM


class VMS(object):

    def __init__(self):
        self.pve_web = Config["pve_web"]
        self.pve_ssh = Config["pve_ssh"]
        self.node = Config["node"]
        self.proxmox = ProxmoxAPI(
            self.pve_web[0], user=self.pve_web[1], password=self.pve_web[3], verify_ssl=False, port=self.pve_web[2]
        )
        self.vmStatus = self.proxmox('nodes')(self.node)('qemu').get()
        trans = paramiko.Transport((self.pve_ssh[0], self.pve_ssh[2]))
        trans.connect(username=self.pve_ssh[1], password=self.pve_ssh[3])

        # 将sshclient的对象的transport指定为以上的trans
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = trans

        # 剩下的就和上面一样了
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.timeSleep = 1

    def getVM(self):
        res = []
        for vm in self.vmStatus:
            res.append([vm["vmid"], vm["name"]])
        return res
    def stopPve(self):

        for qm in self.vmStatus:
                print("name : {} vmid : {} status: {}".format(qm["name"], qm["vmid"], qm["status"]))
                if qm["status"] == "running":
                    vmnode=VM(qm["vmid"])
                    vmnode.stop()
                    time.sleep(2)
                    vmnode.shutdown()
                    time.sleep(2)
                if qm["status"] == "running":
                    vmnode=VM(qm["vmid"])
                    vmnode.forceStop()

    def rebootPve(self):
        self.stopPve()
        time.sleep(5)
        self.ssh.exec_command("reboot")



# if __name__ == '__main__':
#     res = VMS().getVM()
#     res.sort()
#     print(res)
