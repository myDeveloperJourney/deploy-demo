"""Search agent — DuckDuckGo wrapper, ReAct pattern.

Same shape as Lab 4.4's SearchAgent. DDG is rate-limit-friendly and
doesn't require an API key, which makes it a good fit for a public demo.
"""
from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_openai import ChatOpenAI


class SearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.search = DuckDuckGoSearchAPIWrapper()
        self.tools = [
            Tool(
                name="web_search",
                func=self.search.run,
                description=(
                    "Searches the web for current information using DuckDuckGo. "
                    "Use this for any question about current events, news, "
                    "or facts not in the model's training data. "
                    "Input should be a concise search query string."
                ),
            ),
        ]
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )

    def run(self, question: str) -> str:
        return self.agent.run(question)
