from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

#load_dotenv("../.env")

# CMCPサーバーの作成
mcp = FastMCP(
    name="Calculator",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

# シンプルなツールadd 
@mcp.tool()
def add(a: int, b: int) -> int:
    """2つの数字を足す"""
    return a + b

# シンプルなツールmul
@mcp.tool()
def mul(c: int, d: int) ->int:
    "2つの数字を掛け合わせる"
    return c*d

# シンプルなツールcat 
@mcp.tool()
def cat(familyname: str, surname: str) ->str:
    "2つの文字列を連結する"
    return f"{surname} {familyname}"
 
# Run the server
if __name__ == "__main__":
    transport = "studio"
    if transport == "stdio":
        print("stdioトランスポートでサーバーを実行")
        mcp.run(transport="stdio")
    elif transport == "sse":
        print("SSEトランスポートでサーバーを実行")
        mcp.run(transport="sse")
    else:
        raise ValueError(f"不明なトランスポート: {transport}")