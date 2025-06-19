import asyncio
import gradio as gr
import openai
from dotenv import load_dotenv
from mcpclient import MCPOpenAIClient
load_dotenv("../.env")
client = openai.OpenAI()

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
