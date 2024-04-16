from pipesocket import ClientPipeSocket
from IPython import embed

if __name__ == "__main__":
    pipe = ClientPipeSocket(host_ip='192.168.1.10', host_port=5555)
    embed()
