
import time

import paramiko
from proxmoxer import ProxmoxAPI
from config import Config


class VM(object):

    def __init__(self, vmid):

        self.vmid = vmid
        self.pve_web = Config["pve_web"]
        self.pve_ssh = Config["pve_ssh"]
        self.node = Config["node"]
        self.proxmox = ProxmoxAPI(
            self.pve_web[0], user=self.pve_web[1], password=self.pve_web[3], verify_ssl=False, port=self.pve_web[2]
        )
        self.vm=  self.proxmox('nodes')(self.node)('qemu')(self.vmid)
        self.vmStatus = self.proxmox('nodes')(self.node)('qemu')(self.vmid)('status')


        trans = paramiko.Transport((self.pve_ssh[0], self.pve_ssh[2]))
        trans.connect(username=self.pve_ssh[1], password=self.pve_ssh[3])

        # 将sshclient的对象的transport指定为以上的trans
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = trans

        # 剩下的就和上面一样了
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.timeSleep = 1

    def stop(self):
        self.vmStatus('stop').post()

    def shutdown(self):
        self.vmStatus('shutdown').post()

    def reboot(self):
        self.vmStatus('reboot').post()

    def start(self):
        self.vmStatus('start').post()


    def current(self):
        vm_info = self.vmStatus('current').get()

        # for i, k in data.items():
        #     print(i, k)
        formatted_info = [
            f"🖥️ <b>VM ID:</b> {vm_info['vmid']}",
            f"🏷️ <b>Name:</b> {vm_info['name']}",
            f"🔢 <b>CPUs:</b> {vm_info['cpus']}",
            f"🧠 <b>Memory:</b> {vm_info['maxmem'] / 1024 / 1024} MB",
            f"💽 <b>Disk Size:</b> {vm_info['maxdisk'] / 1024 / 1024 / 1024} GB",
            f"⏲️ <b>Uptime:</b> {vm_info['uptime']} seconds",
            f"🔌 <b>Status:</b> {vm_info['status'].capitalize()}",
            f"📶 <b>Network In:</b> {vm_info['netin']}",
            f"📶 <b>Network Out:</b> {vm_info['netout']}",
            f"💾 <b>Disk Read:</b> {vm_info['diskread']}",
            f"💾 <b>Disk Write:</b> {vm_info['diskwrite']}",
            f"🖥️ <b>QMP Status:</b> {vm_info['qmpstatus'].capitalize()}",
            f"🔌 <b>High Availability:</b> {'Enabled' if vm_info['ha']['managed'] else 'Disabled'}"
        ]

        return "\n".join(formatted_info)

    def forceStop(self):

        self.ssh.exec_command("rm -rf /run/lock/qemu-server/lock-{}.conf".format(self.vmid))
        self.ssh.exec_command("qm unlock {}".format(self.vmid))
        time.sleep(self.timeSleep)

        self.ssh.exec_command("qm stop {}".format(self.vmid))







# if __name__ == '__main__':
#     test = VM(111)
#     test.current()
