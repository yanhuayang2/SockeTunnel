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


def connect(host: str, port: int, num: int):
    max_retries = 10
    retry_delay = 5
    retry_count = 0

    while True:
        if retry_count > max_retries:
            streams[num] = 'quit'
            logging.error(f'Failed to connect to {host}:{port} after {max_retries} attempts')

        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
        except Exception as e:
            logging.warning(f'Cannot connect to {host}:{port} - Attempt {retry_count + 1}/{max_retries}')
            retry_count += 1
            time.sleep(retry_delay)
            continue

        logging.info(f'Connected to {host}:{port}')
        streams[num] = conn
        s2 = get_another_stream(num)
        exchange_stream(num, conn, s2)


def main():
    parser = argparse.ArgumentParser(description="Client End | Cmd eg. "
                                                 "python client.py 127.0.0.1:1234 127.0.0.1:8081")
    parser.add_argument('public_server', type=str, help='Public address')
    parser.add_argument('intranet_addr', type=str, help='Intranet service address')
    args = parser.parse_args()

    public_addr = args.public_server.split(':')
    PORT_MAP[0] = int(public_addr[1])
    t = threading.Thread(target=connect, args=(public_addr[0], int(public_addr[1]), 0))

    intranet_addr = args.intranet_addr.split(':')
    PORT_MAP[1] = int(intranet_addr[1])
    i = threading.Thread(target=connect, args=(intranet_addr[0], int(intranet_addr[1]), 1))

    t.start()
    i.start()
    t.join()
    i.join()


if __name__ == '__main__':
    main()