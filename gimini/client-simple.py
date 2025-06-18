import asyncio
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List
import os 
import re
import nest_asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai

# nest_asyncioを適用してネストされたイベントループを許可する（Jupyter/IPythonで必要）
nest_asyncio.apply()

# 環境変数をロードする
load_dotenv("../.env")

# セッション状態を保存するためのグローバル変数
session = None
exit_stack = AsyncExitStack()

# Initialize Gemini Model
genai.configure(api_key=os.getenv("GIMINI_API_KEY"))  # or set via .env and os.getenv
model = genai.GenerativeModel("gemini-2.5-flash")

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
    global session,model

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

# Google Mimini APIを使用する 
async def process_query(query: str) -> str:
    global session, model

    tools = await get_mcp_tools()
    
    # 初期応答を生成する
    prompt = f"User query: {query}\nAvailable tools:\n"
    for tool in tools:
        func = tool["function"]
        prompt += f"- {func['name']}: {func['description']}\n"

    prompt += """You are a tool-calling assistant.
            Given a user query and a list of available tools, decide the best tool to use and its arguments and return only a JSON object in the format:
            {"tool": string, "arguments": object}
            """
    response = model.generate_content(prompt)

    content = response.text
    
    try:
        cleaned = content.replace("```json", "").replace("```", "")
                
        tool_response = json.loads(cleaned)
        
        tool_name = tool_response["tool"]
        arguments = tool_response["arguments"]
    
        # ツールコールの実行
        result = await session.call_tool(tool_name, arguments)
    
        # ツールの結果をジェミニに送り、最終的な回答を得る
        final_prompt = f"User asked: {query}\nTool '{tool_name}' was used and returned: {result.content[0].text}\nPlease generate a final exact response."
        final_response = model.generate_content(final_prompt)
        return final_response.text
    
    except (json.JSONDecodeError, KeyError):
        # No valid tool response, just return original
        return f"can not find tool with response {content}"


async def cleanup():
    """クリーンアップ・リソース."""
    global exit_stack
    await exit_stack.aclose()


async def main():
    """クライアントのメイン・エントリー・ポイント"""
    await connect_to_server("server.py")

    # 例 会社の休暇制度について尋ねる
    query = "当社の休暇制度について教えてください。"
    print(f"\nQuery: {query}")

    response = await process_query(query)
    print(f"\nレスポンス: {response}")

    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
