from google.adk.agents.llm_agent import Agent
from .tools.sales_tool import get_business_data

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for administrative questions about the bussiness AICLOUD.',
    instruction="""
    Answer user questions to the best of your knowledge, the information can be only obtained using the provided tools, don\'t answer questions that aren\' about my bussiness AICLOUD Cambio.
    """,
    tools=[get_business_data]
)
