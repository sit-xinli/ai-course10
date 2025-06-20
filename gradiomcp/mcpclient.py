
import json
from contextlib import AsyncExitStack
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import AsyncOpenAI


# 環境変数をロードする
load_dotenv("../.env")

class MCPOpenAIClient:
    """MCPツールを使ってOpenAIのモデルと対話するためのクライアント."""

    def __init__(self, model: str = "gpt-4.1-nano"):
        """OpenAI MCPクライアントを初期化する.

        Args:
            model: 使用するOpenAIモデル.
        """
        # セッションとクライアントのオブジェクトを初期化する
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai_client = AsyncOpenAI()
        self.model = model
        self.stdio: Optional[Any] = None
        self.write: Optional[Any] = None
        self.running = False
        
    async def connect_to_server(self, server_script_path: str = "server.py"):
        """MCPサーバーに接続する.

        Args:
            server_script_path: サーバースクリプトへのパス.
        """
        # Server configuration
        server_params = StdioServerParameters(
            command="python",
            args=[server_script_path],
        )

        # サーバーに接続する
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # 接続の初期化
        await self.session.initialize()

        tools_result = await self.session.list_tools()
        print("\nConnected to server with tools:")
        for tool in tools_result.tools:
            print(f"  - {tool.name}: {tool.description}")

        self.running = True
        
              
    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """MCPサーバーから利用可能なツールをOpenAIフォーマットで取得する.

        Returns:
            OpenAI形式のツールリスト.
        """
        
        tools_result = await self.session.list_tools()
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

    async def process_query(self, query: str) -> str:
        """OpenAIと利用可能なMCPツールを使用してクエリを処理する.

        Args:
            query: ユーザークエリ.

        Returns:
            OpenAIからの回答.
        """
        # 利用可能なツールを入手する
        tools = await self.get_mcp_tools()

        # IOpenAI APIコール
        response = await self.openai_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": query}],
            tools=tools,
            tool_choice="auto",
        )
        
        # アシスタントの返答を得る
        assistant_message = response.choices[0].message
        print(f"--------------{assistant_message}-------------")
        # ユーザーからの問い合わせとアシスタントの応答による会話の初期化
        messages = [
            {"role": "user", "content": query},
            assistant_message,
        ]

        # ツールコールがある場合はそれを処理する
        if assistant_message.tool_calls:
            # 各ツールの呼び出しを処理する
            for tool_call in assistant_message.tool_calls:
                # ツールコールの実行
                result = await self.session.call_tool(
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
            final_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="none",  # Don't allow more tool calls
            )

            return final_response.choices[0].message.content

        # ツールの呼び出しはなく、LLMから直接レスポンスを返すだけ
        return assistant_message.content

    async def cleanup(self):
        """クリーンアップ・リソース."""
        await self.exit_stack.aclose()

