# uv add langchain-openai dotenv
# uv add -U langchain-community

from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents import Tool, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.agents.react.agent import create_react_agent
from langchain.agents.react.base import get_prompt
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

# Define tools the agent can use
search_tool = DuckDuckGoSearchRun()
tools = [
    Tool(
        name="Search",
        func=search_tool.run,
        description="Useful for searching the internet for current information"
    )
]

# Initialize the language model
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.0)

# Define the prompt template with all required variables
prompt = get_prompt()


# Create the agent with the React framework
agent = create_react_agent(llm, tools, prompt=prompt)

# Create an agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
response = agent_executor.invoke({"input": "What are the latest developments in AI agent frameworks?"})
print(response["output"])
