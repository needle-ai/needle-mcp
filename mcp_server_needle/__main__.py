import asyncio
from .server import NeedleMCPServer

async def main():
    server = NeedleMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main()) 