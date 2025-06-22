# uv add mcp nest_asyncio asyncio

import asyncio
import nest_asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

nest_asyncio.apply()  # Needed to run interactive python

"""
確認：
1. このスクリプトを実行する前に、サーバーが稼動していることを確認します。
2. サーバーがSSEトランスポートを使用するように構成されている。
3. サーバーがポート8050をリッスンしている。

サーバーを実行するには
uv run server.py
"""


async def main():
    # SSEを使ってサーバーに接続する
    async with sse_client("http://localhost:8050/sse") as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 接続の初期化
            await session.initialize()

            # 使用可能なツールのリスト
            tools_result = await session.list_tools()
            print("利用可能なツール:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # MCPプロトコルによりツールを利用
            result = await session.call_tool("cat", arguments={"surname": "Li", "familyname": "Xinxiao"})
            print(f"My name is {result.content[0].text}")


if __name__ == "__main__":
    asyncio.run(main())
