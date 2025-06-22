#uv add camel-ai[web-tools]
#
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.typing import ModelType
import asyncio

async def main():
    # Create two agents with different roles
    user_agent = ChatAgent(
        model_type=ModelType.GPT_4,
        system_message="You are a user who needs help analyzing data about AI frameworks."
    )
    
    assistant_agent = ChatAgent(
        model_type=ModelType.GPT_4,
        system_message="You are an AI assistant specialized in data analysis and AI frameworks."
    )
    
    # Initial message from the user agent
    user_message = BaseMessage.make_user_message(
        role_name="User",
        content="I need to compare different AI agent frameworks for my project. Can you help me analyze their features?"
    )
    
    # Start the conversation
    assistant_response = await assistant_agent.step(user_message)
    print(f"Assistant: {assistant_response.content}\n")
    
    # Continue the conversation
    for _ in range(3):  # Simulate a few turns of conversation
        user_response = await user_agent.step(assistant_response)
        print(f"User: {user_response.content}\n")
        
        assistant_response = await assistant_agent.step(user_response)
        print(f"Assistant: {assistant_response.content}\n")
if __name__ == "__main__":
    asyncio.run(main())