import asyncio
import gradio as gr
from dotenv import load_dotenv
from mcpclient import MCPOpenAIClient
load_dotenv("../.env")

client = MCPOpenAIClient()


"""
def chat(user_input, history):
    history.append({"role": "user", "content": user_input})
    
    response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=history
        )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})

    # 履歴を Markdown 形式で整形
    chat_log = ""
    for msg in history:
        if msg["role"] == "user":
            chat_log += f"**🧑 ユーザー:** {msg['content']}\n\n"
        elif msg["role"] == "assistant":
            chat_log += f"**🤖 アシスタント:** {msg['content']}\n\n"


    return "", reply, history, chat_log


def respond(user_input, history):
    _, bot_msg, updated_history, chat_log = chat(user_input, history)
    return "", bot_msg, updated_history, chat_log

with gr.Blocks() as demo:
    gr.Markdown("## 💬 私のOpenAI チャット")

    with gr.Row():
        with gr.Column():
            user_text = gr.Textbox(label="ユーザーの入力", placeholder="質問を入力してください")
        with gr.Column():
            bot_response = gr.Textbox(label="LLMの応答", interactive=False)

    chat_history_display = gr.Markdown()
    state = gr.State([])

    user_text.submit(respond, [user_text, state], [user_text, bot_response, state,chat_history_display])

    demo.launch(share=True)
"""

async def ask_mcp_async(prompt):  
    ## Connect to the MCP server
    await client.connect_to_server("server.py")
    print("Connected to MCP server.")
      
    return await client.process_query(prompt)

def ask_mcp_sync(prompt):
    try:
        loop = asyncio.get_event_loop()
        print(f"##############################Current event loop: {loop}")
        if loop.is_running():
            # Create a new task and wait for it
            future = asyncio.ensure_future(ask_mcp_async(prompt))
            return asyncio.get_event_loop().run_until_complete(future)
        else:
            return loop.run_until_complete(ask_mcp_async(prompt))
    except RuntimeError:
        return asyncio.run(ask_mcp_async(prompt))


print("Starting Gradio UI...")
gr.Interface(
    fn=ask_mcp_sync,
    inputs=gr.Textbox(lines=2, placeholder="Enter your prompt here..."),
    outputs="text",
    title="MCP Chatbot UI",
    description="Talk with an MCP-connected model via Gradio",
).launch()