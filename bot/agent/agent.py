import re
import json
from uuid import uuid4

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END

from .models import llm
from .memory import State, summarize_conversation, memory
from .tools import *

class Agent:
    def __init__(self):
        self.system_prompt = '''Your name is Severus, you are a smart AI assistant and answers the user questions intelligently. You can answer the user questions directly using your own knowledge and information from the earlier conversation messages or you can also use the tools provided to you. These tools can perform specific tasks by giving appropriate inputs, fetch data and information to answer the user questions more accurately.
                ## Guidance:
                1. If you are not able to answer the user question you can ask the user for more information or to elaborate the question.
                2. After getting response from the tool (only if you executed any tool calls), return the final answer of the user's questions.
                3. If the tools returns any error. You can try calling the tools again and then return the final answer. Strictly do not call the tool for more than three times to answer the same user question.
                '''

        self.tools_dict = {"multiplication_tool" : multiplication_tool, "retrieval_tool" : retrieval_tool}
        for tool in gmail_tools:
            self.tools_dict[tool.name] = tool

        self.llm_with_tools = llm.bind_tools(list(self.tools_dict.values()))
        self.agent = self.build_agent()

    def call_model(self, state: State):
        system_message = self.system_prompt
        summary = state.get("summary", "")
        if summary:
            summary_message = f'''
                ## Summary of the earlier conversation :
                {summary}
                '''
            system_message += summary_message
        
        messages = [SystemMessage(content=system_message)] + state["messages"]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def call_tools(self, state: State):
            messages = state["messages"]
            try:
                tool_call = messages[-1].tool_calls[0]
            except:
                tool_call = self.extract_tool_info(messages[-1].content)

            try:
                print(f"Calling Tool : {tool_call["name"]}")
                tool = self.tools_dict[tool_call["name"]]
                tool_output = tool.invoke(tool_call["args"])

            except Exception as e:
                tool_output = "Error occured when calling the tool. Please provide correct input for the tool"
                print(f"Error : {e}")

            tool_response = ToolMessage(content=tool_output, tool_call_id=tool_call["id"])
            return {"messages" : [tool_response]}


    def should_continue(self, state: State):
        """Return the next node to execute."""

        messages = state["messages"]
        if messages[-1].tool_calls:
            return "call_tools"

        pattern = r"<function=(\w+)(\{.*?\})</function>"
        match = re.search(pattern, messages[-1].content)
        if match:
            return "call_tools"

        if len(messages) > 10:
            return "summarize_conversation"
        return END

    def extract_tool_info(self, response):
            pattern = r"<function=(\w+)(\{.*?\})</function>"
            match = re.search(pattern, response)
            if match:
                tool_name = match.group(1)
                tool_args = json.loads(match.group(2))
                return {"name": tool_name, "args": tool_args, "id": str(uuid4())[:8]}
            return None

    def build_agent(self):
        workflow = StateGraph(State)

        workflow.add_node("call_model", self.call_model)
        workflow.add_node("call_tools", self.call_tools)
        workflow.add_node("summarize_conversation", summarize_conversation)

        workflow.add_edge(START, "call_model")
        workflow.add_conditional_edges("call_model", self.should_continue)
        workflow.add_edge("call_tools", "call_model")
        workflow.add_edge("summarize_conversation", END)

        agent = workflow.compile(checkpointer=memory)
        return agent

    def get_response(self, query, session_id=0):
            try:
                config = {"configurable": {"thread_id": f"{session_id}"}}

                user_message = HumanMessage(content= query.strip())
                response = self.agent.invoke({"messages": [user_message]}, config)

                return response["messages"][-1].content
            except Exception as e:
                return f"Error: {str(e)}"
