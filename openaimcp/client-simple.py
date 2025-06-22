# uv add mcp dotenv openai nest_asyncio asyncio contextlib

import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List

import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI

# nest_asyncioを適用してネストされたイベントループを許可する（Jupyter/IPythonで必要）
nest_asyncio.apply()

# 環境変数をロードする
load_dotenv("../.env")

# セッション状態を保存するためのグローバル変数
session = None
exit_stack = AsyncExitStack()
openai_client = AsyncOpenAI()
model = "gpt-4.1-nano"

async def connect_to_server(server_script_path: str = "server.py"):
    """MCPサーバーに接続する.

    Args:
        server_script_path: サーバースクリプトへのパス.
    """
    global session, exit_stack

    # サーバー構成
    server_params = StdioServerParameters(
        command="python",
        args=[server_script_path],
    )

    # サーバーに接続する
    stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
    stdio, write = stdio_transport
    session = await exit_stack.enter_async_context(ClientSession(stdio, write))

    # 接続の初期化
    await session.initialize()

    # 使用可能なツールのリスト
    tools_result = await session.list_tools()
    print("\nツールでサーバーに接続:")
    for tool in tools_result.tools:
        print(f"  - {tool.name}: {tool.description}")


async def get_mcp_tools() -> List[Dict[str, Any]]:
    """MCPサーバーから利用可能なツールをOpenAIフォーマットで取得する.

    Returns:
        OpenAI形式のツールリスト.
    """
    global session

    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in tools_result.tools
    ]


async def process_query(query: str) -> str:
    """OpenAIと利用可能なMCPツールを使用してクエリを処理する.

    Args:
        query: The user query.

    Returns:
        OpenAIからの回答.
    """
    global session, openai_client, model

    # 利用可能なツールを入手する
    tools = await get_mcp_tools()
    
    # 最初のOpenAI APIコール
    response = await openai_client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": query}],
        tools=tools,
        tool_choice="auto",
    )

    # アシスタントの返答を得る
    assistant_message = response.choices[0].message

    # ユーザーの問い合わせとアシスタントの応答で会話を初期化する
    messages = [
        {"role": "user", "content": query},
        assistant_message,
    ]

    # ツールコールがある場合はそれを処理する
    if assistant_message.tool_calls:
        # 各ツールの呼び出しを処理する
        for tool_call in assistant_message.tool_calls:
            # ツールコールの実行 (MCPプロトコル)
            result = await session.call_tool(
                tool_call.function.name,
                arguments=json.loads(tool_call.function.arguments),
            )

            # 会話にツールの反応を追加
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content[0].text,
                }
            )

        # OpenAIからツール結果の最終応答を得る
        final_response = await openai_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="none",  # これ以上のツールコールを許さない
        )

        return final_response.choices[0].message.content

    # ツールの呼び出しはなく、ダイレクト・レスポンスを返すだけ
    return assistant_message.content


async def cleanup():
    """クリーンアップ・リソース."""
    global exit_stack
    await exit_stack.aclose()


async def main():
    """クライアントのメイン・エントリー・ポイント"""
    await connect_to_server("server.py")

    # 例 会社の休暇制度について尋ねる
    query = "当社の休暇制度について?"
    print(f"\nQuery: {query}")

    response = await process_query(query)
    print(f"\nレスポンス: {response}")

    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
