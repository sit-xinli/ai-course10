from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Initialize the language model
llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0.5)
# Define agents with specific roles
researcher = Agent(
    role="リサーチ・アナリスト",
    goal="AI技術の最新トレンドを発見し、分析する",
    backstory="AI研究のエキスパートであり、新たなトレンドに敏感な方",
    verbose=True,
    llm=llm
)
writer = Agent(
    role="テクニカルライター",
    goal="調査結果に基づく包括的なレポートの作成s",
    backstory="複雑なコンセプトを明確に説明できる熟練したテクニカルライター",
    verbose=True,
    llm=llm
)
# Define tasks for each agent
research_task = Task(
    description="AIエージェントフレームワークの最新動向を研究",
    expected_output="現在のAIエージェントフレームワークの包括的分析",
    agent=researcher
)
writing_task = Task(
    description="調査に基づき、AIエージェントのフレームワークに関する詳細なレポートを作成する。",
    expected_output="AIエージェントのフレームワークに関する体系的なレポート",
    agent=writer,
    context=[research_task]  # The writing task depends on the research task
)
# Create a crew with the agents and tasks
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True
)
# Execute the crew's tasks
result = crew.kickoff()
print(result)
