from pipesocket import ServerPipeSocket
from IPython import embed

if __name__ == "__main__":
    pipe = ServerPipeSocket(host_ip='192.168.1.10', host_port=5555)
    embed()