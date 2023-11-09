import socket
import config_loader

content = config_loader.loadYaml()
HOST = '0.0.0.0'
PORT = int(content['PORT'])

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            data = conn.recv(1024)
            returnVal = data.decode()
            print(returnVal)
            if not data:
                break
            conn.sendall(data)
            conn.close

if __name__ == "__main__":
    main()