"""Search agent — DuckDuckGo wrapper, ReAct pattern.

Same shape as Lab 4.4's SearchAgent. DDG needs no API key, but it
rate-limits datacenter IPs (e.g. Railway), so a deployed instance will
periodically get throttled. The web_search tool therefore catches those
failures and returns a message the agent can act on, rather than letting
a RatelimitException crash the whole workflow.
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
                func=self._search,
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
            max_iterations=25,
        )

    def _search(self, query: str) -> str:
        """Run a DDG search, returning a clean message instead of raising.

        DuckDuckGo throttles datacenter IPs, so a public deployment will
        periodically get rate-limited. Rather than crash the workflow with
        a traceback, return an Observation the ReAct agent can act on — it
        will fall back to answering from model knowledge.
        """
        try:
            return self.search.run(query)
        except Exception as exc:  # noqa: BLE001 — keep the demo alive
            if "ratelimit" in type(exc).__name__.lower() or "ratelimit" in str(exc).lower():
                return (
                    "Web search is temporarily rate-limited and returned no "
                    "results. Answer the question from your own knowledge, "
                    "and note that live search results were unavailable."
                )
            return (
                f"Web search failed ({type(exc).__name__}: {exc}). Answer "
                "from your own knowledge if possible, and note that search "
                "was unavailable."
            )

    def run(self, question: str) -> str:
        return self.agent.run(question)
