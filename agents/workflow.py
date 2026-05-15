"""AgentWorkflow — deterministic router across three agents.

This is the same shape as Lab 4.4's AgentWorkflow. The classifier is
intentionally simple keyword matching — same logic students wrote in the
lab. The point is to show that an orchestrator is just a plain function
that picks an agent; it isn't magical.

If task_type is passed in explicitly ('math', 'sql', 'search'), the
classifier is skipped. That lets the demo UI force a specific agent for
controlled walkthroughs.
"""
from .math_agent import MathAgent
from .search_agent import SearchAgent
from .sql_agent import SQLAgent


class AgentWorkflow:
    def __init__(self, db_path: str = "data/sample.db"):
        self.math = MathAgent()
        self.sql = SQLAgent(db_path)
        self.search = SearchAgent()

    def run(self, question: str, task_type: str = "auto") -> str:
        if task_type == "auto":
            task_type = self._classify(question)

        if task_type == "math":
            return self.math.run(question)
        if task_type == "sql":
            return self.sql.run(question)
        if task_type == "search":
            return self.search.run(question)
        raise ValueError(f"Unknown task type: {task_type!r}")

    @staticmethod
    def _classify(question: str) -> str:
        q = question.lower()
        math_kw = (
            "plus", "minus", "times", "divided", "square root",
            "add ", "subtract", "multiply", "calculate",
            "+", "-", "*", "/", "what is ", "compute",
        )
        sql_kw = (
            "how many", "list ", "show me", "select ", "customers",
            "orders", "products", "table", "database", "rows",
            "total", "sum of", "average", "revenue", "top ",
        )
        search_kw = (
            "news", "latest", "current", "today", "weather",
            "who is", "what's happening", "search for", "find articles",
            "recent", "headlines",
        )
        # Order matters: SQL keywords are checked before math to catch
        # "show me total orders" before "total" pings as math.
        if any(k in q for k in sql_kw):
            return "sql"
        if any(k in q for k in math_kw):
            return "math"
        if any(k in q for k in search_kw):
            return "search"
        # Fallback: send unknown queries to search since DDG has broad coverage.
        return "search"
