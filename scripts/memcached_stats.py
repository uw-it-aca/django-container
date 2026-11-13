import socket
import argparse


class SimpleMemcachedClient:
    def __init__(self, host="127.0.0.1", port=11211):
        self.host = host
        self.port = port

    def _send_command(self, cmd: bytes) -> bytes:
        """Helper to open a socket, send a command, and read the response."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(cmd)

            # Read response chunks until the buffer clears
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
                # Text protocol ends transmission with specific markers
                if (response.endswith(b"END\r\n") or response.endswith(b"STORED\r\n") or
                        response.endswith(b"NOT_STORED\r\n") or response.endswith(b"ERROR\r\n")):
                    break

            return response

    def stats(self):
        cmd = "stats\r\nquit".encode('utf-8')
        response = self._send_command(cmd)
        return response.decode('utf-8')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Memcached Client")
    parser.add_argument('host', nargs=1, help="memcached hostname")
    args = parser.parse_args()

    client = SimpleMemcachedClient(host=args.host[0])
    print(client.stats())
