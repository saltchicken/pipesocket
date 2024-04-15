from pipesocket import PipeSocket
from IPython import embed

if __name__ == "__main__":
    pipe = PipeSocket(True)
    embed()