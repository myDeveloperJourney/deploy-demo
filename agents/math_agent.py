"""Math agent — five arithmetic tools, ReAct pattern.

Same shape as Lab 4.4's MathAgent. Each tool has Name + Function + Description;
the model reads the descriptions to pick which one to call.
"""
import math

from langchain.agents import AgentType, initialize_agent
from langchain.tools import Tool
from langchain_openai import ChatOpenAI


def parse_two_numbers(s: str):
    parts = [p.strip() for p in s.split(",")]
    return float(parts[0]), float(parts[1])


class MathAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.tools = [
            Tool(
                name="Addition",
                func=lambda s: sum(parse_two_numbers(s)),
                description="Adds two numbers together. Input should be two numbers separated by a comma.",
            ),
            Tool(
                name="Subtraction",
                func=lambda s: parse_two_numbers(s)[0] - parse_two_numbers(s)[1],
                description="Subtracts the second number from the first. Input should be two numbers separated by a comma.",
            ),
            Tool(
                name="Multiplication",
                func=lambda s: parse_two_numbers(s)[0] * parse_two_numbers(s)[1],
                description="Multiplies two numbers together. Input should be two numbers separated by a comma.",
            ),
            Tool(
                name="Division",
                func=lambda s: parse_two_numbers(s)[0] / parse_two_numbers(s)[1],
                description="Divides the first number by the second. Input should be two numbers separated by a comma.",
            ),
            Tool(
                name="Square_Root",
                func=lambda s: math.sqrt(float(s)),
                description="Returns the square root of a number. Input should be a single number.",
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

    def run(self, question: str) -> str:
        return self.agent.run(question)
