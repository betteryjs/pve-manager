# https://pve.proxmox.com/pve-docs/api-viewer/index.html#/nodes/{node}
# https://proxmoxer.github.io/docs/2.0/




## 在机子上安装python

```
apt install python3-pip python3-venv
```

## 创建虚拟环境 venv
```
python3 -m venv .venv
source .venv/bin/activate
```


## install requirements.txt

```
pip install -r requirements.txt
```