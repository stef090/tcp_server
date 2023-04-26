import asyncio


class Client:
    def __init__(self, pid):
        self.reader = None
        self.writer = None
        self.pid = pid

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection("127.0.0.1", 8888)

    async def start(self):
        message = f"PID:{self.pid}"
        await self.send_message(message)
        await asyncio.sleep(0.5)
        await self.send_message("PING")
        while self.reader is not None:
            await asyncio.sleep(0.01)
            data = await self.reader.read(100)
            received_message = f"{data.decode()}"
            if received_message is not None and received_message != "":
                print(f"Received for PID: {self.pid}, message: {received_message}")
                await self.send_message("PING")

    async def send_message(self, message: str):
        message = message + "\r"
        self.writer.write(message.encode())
        await self.writer.drain()

    async def stop(self):
        self.reader = None
        self.writer.close()
        await self.writer.wait_closed()


async def run_client(token):

    clients = []
    for i in range(100):
        client = Client(f"{i}")
        await client.connect()
        clients.append(client)

    await asyncio.gather(*[c.start() for c in clients])


if __name__ == "__main__":
    asyncio.run(run_client("Message sending..."))