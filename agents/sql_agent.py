"""SQL agent — same shape as Lab 4.4, plus read-only safety guards.

Production-bound version. The lab's SQL agent was deliberately permissive
so students could see the unguarded pattern; this one demonstrates the
"Tool guardrails" tier from the 5-tier framework (Day 4 slide 49 and
Day 5 slide 20):

  - Only SELECT statements allowed
  - DROP / DELETE / UPDATE / INSERT / ALTER / TRUNCATE / CREATE / ATTACH
    / DETACH / PRAGMA all rejected via regex
  - Auto-injects LIMIT 100 if the query omits one (rate-limits result size)
  - Wraps every execution in try/except so a malformed query never crashes
    the worker

If a student asks "why did you add those guards in production but not in
the lab?" — the answer is: the lab is a teaching artifact, the deployed
version is a public endpoint. Tools you ship to production need
validation, error handling, and limits. The lab's permissive version was
intentional — to show what NOT to do.
"""
import re
import sqlite3

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

UNSAFE_PATTERNS = re.compile(
    r"\b(drop|delete|update|insert|alter|truncate|create|attach|detach|pragma|replace)\b",
    re.IGNORECASE,
)


class SQLAgent:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.tools = [
            Tool(
                name="describe_schema",
                func=self._describe,
                description=(
                    "Returns the schema of all tables in the database. "
                    "Always use this first to understand what data is available. "
                    "No input needed — pass an empty string."
                ),
            ),
            Tool(
                name="execute_query",
                func=self._execute,
                description=(
                    "Executes a read-only SQL SELECT query against the database. "
                    "Input should be a valid SQL SELECT statement. "
                    "Only SELECT queries are allowed; any other statement type will be rejected. "
                    "Results are limited to 100 rows."
                ),
            ),
        ]
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=6,
        )

    def _execute(self, query: str) -> str:
        if UNSAFE_PATTERNS.search(query):
            return "Error: only SELECT queries are allowed. Statement rejected by guardrail."
        if not query.strip().lower().lstrip("(").startswith("select"):
            return "Error: only SELECT queries are allowed."
        # Auto-LIMIT to keep responses bounded.
        if "limit" not in query.lower():
            query = query.rstrip(";").rstrip() + " LIMIT 100"
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            con.close()
            if not rows:
                return "No rows returned."
            header = " | ".join(cols)
            body = "\n".join(" | ".join(str(c) for c in r) for r in rows[:50])
            extra = f"\n... and {len(rows) - 50} more rows" if len(rows) > 50 else ""
            return f"{header}\n{body}{extra}"
        except sqlite3.Error as e:
            return f"SQL error: {e}"

    def _describe(self, _: str = "") -> str:
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [r[0] for r in cur.fetchall()]
            lines = []
            for t in tables:
                cur.execute(f"PRAGMA table_info({t})")
                cols = cur.fetchall()
                col_desc = ", ".join(f"{c[1]} ({c[2]})" for c in cols)
                lines.append(f"Table {t}: {col_desc}")
            con.close()
            return "\n".join(lines) if lines else "No tables found."
        except sqlite3.Error as e:
            return f"Schema error: {e}"

    def run(self, question: str) -> str:
        return self.agent.run(question)
