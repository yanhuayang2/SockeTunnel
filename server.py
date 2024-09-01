import socket
import sys
import threading
import time
import logging
import argparse

streams = [None, None]
PORT_MAP = {}
DEBUG = False
logging.basicConfig(level=logging.INFO if DEBUG else logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

PORT_MAP = {}

def exchange_stream(num: int, s1: socket.socket, s2: socket.socket):
    try:
        while True:
            buff = s1.recv(1024)
            if len(buff) == 0:
                logging.info(f'{PORT_MAP[num]} one closed')
                break
            s2.sendall(buff)
            logging.debug(f'{PORT_MAP[num]} data exchanged')
    except Exception:
        logging.info(f'{PORT_MAP[num]} connection closed')

    finally:
        try:
            s1.shutdown(socket.SHUT_RDWR)
            s1.close()
        except:
            pass
        try:
            s2.shutdown(socket.SHUT_RDWR)
            s2.close()
        except:
            pass
        streams[0] = None
        streams[1] = None
        logging.info(f'{PORT_MAP[num]} CLOSED')


def get_another_stream(num: int):
    other_num = 1 - num

    while True:
        if streams[other_num] == 'quit':
            logging.error('Cannot connect to the target, quitting now!')
            sys.exit(1)

        if streams[other_num] is not None:
            return streams[other_num]
        elif streams[other_num] is None and streams[num] is None:
            logging.info('Stream CLOSED')
            return None
        else:
            time.sleep(1)


def server(port: int, num: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('0.0.0.0', port))
        srv.listen(1)
        while True:
            conn, addr = srv.accept()
            logging.info(f'Connected from: {addr}')
            streams[num] = conn
            s2 = get_another_stream(num)
            exchange_stream(num, conn, s2)


def main():
    parser = argparse.ArgumentParser(description="Server End | Cmd eg. python server.py 1234 1111")
    parser.add_argument('tunnel_port', type=int, help='Intranet connection port')
    parser.add_argument('public_port', type=int, help='External listening port')
    args = parser.parse_args()

    PORT_MAP[0] = args.tunnel_port
    PORT_MAP[1] = args.public_port
    t = threading.Thread(target=server, args=(args.tunnel_port, 0))
    p = threading.Thread(target=server, args=(args.public_port, 1))
    
    p.start()
    t.start()
    p.join()
    t.join()


if __name__ == '__main__':
    main()
