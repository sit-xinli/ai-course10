# uv add mcp

import os
import json
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP(
    name="ナレッジ・ベース",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

@mcp.tool()
def barrow(a: str, b: str) ->str:
    """
    2つの文字列のbarrow計算を定義する。そのほかの計算は定義しない
    returns:
        2つの文字列の変形.
    """
    return f"{a}sit2024commonworkshop{b}"
 
@mcp.tool()
def get_knowledge_base() -> str:
    """SITの知識ＤＢ全体をフォーマットされた文字列として取り出す.

    Returns:
        SITの知識ＤＢからのすべてのQ&Aペアを含むフォーマットされた文字列.
    """
    try:
        kb_path = os.path.join(os.path.dirname(__file__), "data", "kb.json")
        with open(kb_path, "r") as f:
            kb_data = json.load(f)

        # Format the knowledge base as a string
        kb_text = "Here is the retrieved knowledge base:\n\n"

        if isinstance(kb_data, list):
            for i, item in enumerate(kb_data, 1):
                if isinstance(item, dict):
                    question = item.get("question", "Unknown question")
                    answer = item.get("answer", "Unknown answer")
                else:
                    question = f"Item {i}"
                    answer = str(item)

                kb_text += f"Q{i}: {question}\n"
                kb_text += f"A{i}: {answer}\n\n"
        else:
            kb_text += f"Knowledge base content: {json.dumps(kb_data, indent=2)}\n\n"

        return kb_text
    except FileNotFoundError:
        return "Error: 知識ベースファイルが見つかりません"
    except json.JSONDecodeError:
        return "Error: ナレッジ・ベース・ファイルのJSONが無効"
    except Exception as e:
        return f"Error: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
