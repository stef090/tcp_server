import asyncio
import random
from typing import Dict


class Connection:
    def __init__(self, reader, writer, pid):
        self.reader = reader
        self.writer = writer
        self.pid = pid

    async def send_message(self, message):
        self.writer.write(message)
        await self.writer.drain()

    def solve_message(self, message):
        print(f"Message from pid:{self.pid} received: {message}")

    async def listen(self):

        while self.reader:
            await asyncio.sleep(0.01)
            data = await self.reader.read(100)
            message = data.decode()
            if message is not None and message != '':
                print(f"Message received, PID: {self.pid}: {message}")


connections: Dict[str, Connection] = {}
addresses: Dict[str, Connection] = {}


async def handle_message(reader, writer):
    data = await reader.readuntil(b"\r")

    message = data.decode()

    pid = None
    if message.startswith("PID:"):
        pid = message.split("PID:")[-1]

    if pid:
        # PID is SENT
        if pid in connections.keys():
            print("Already connected")
        else:
            connection = Connection(reader, writer, pid)
            connections[pid] = connection
            addr = writer.get_extra_info("peername")
            connections[addr] = connection
            await connection.listen()
    else:
        addr = writer.get_extra_info("peername")
        print(f"No PID sent! {message} on addr: {addr}")


async def random_configuration_change():

    while True:
        await asyncio.sleep(random.uniform(0.0, 0.5))
        if not connections.keys():
            continue
        key = random.choice(list(connections.keys()))
        connection = connections.get(key)
        await connection.send_message("Conf change".encode())


async def start_server():
    server = await asyncio.start_server(handle_message, "127.0.0.1", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await asyncio.gather(*[server.serve_forever(), random_configuration_change()])


if __name__ == "__main__":
    asyncio.run(start_server())