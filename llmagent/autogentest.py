
import autogen
import os
from dotenv import load_dotenv 

# 環境変数をロードする
load_dotenv("../.env")

# Define LLM configuration
llm_config = {
    "config_list": [{
        "model": "gpt-4.1-nano",
        "api_key": os.getenv("OPENAI_API_KEY")
        }],
}
# Create an AssistantAgent
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="あなたは役に立つAIアシスタント。"
)
# Create a UserProxyAgent
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",  # Auto-reply with TERMINATE when the task is done
    max_consecutive_auto_reply=1,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "coding", "use_docker":False},
)
# Initiate chat between agents
user_proxy.initiate_chat(
    assistant,
    message="フィボナッチ数列を計算するPython関数を書く"
)