import asyncio
import gradio as gr
import nest_asyncio
from mcpclient import MCPOpenAIClient

# nest_asyncioを適用してネストされたイベントループを許可する（Jupyter/IPythonで必要）
nest_asyncio.apply()

client = MCPOpenAIClient()

async def chat(user_input, history):
        
    reply = await client.process_query(user_input)

    history.append({"role": "assistant", "content": reply})

    # 履歴を Markdown 形式で整形
    chat_log = ""
    for msg in history:
        if msg["role"] == "user":
            chat_log += f"**🧑 ユーザー:** {msg['content']}\n\n"
        elif msg["role"] == "assistant":
            chat_log += f"**🤖 アシスタント:** {msg['content']}\n\n"


    return "", reply, history, chat_log


async def respond(user_input, history):
    _, bot_msg, updated_history, chat_log = await chat(user_input, history)
    return "", bot_msg, updated_history, chat_log

async def main():
    await client.connect_to_server("server.py") #ok

    #gradio
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

    await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


