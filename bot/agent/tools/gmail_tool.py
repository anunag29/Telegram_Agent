# Literal['add', 'subtract', 'multiply', 'divide']    




# self.sys_prompt = '''You are a smart assistant and answers the user questions intelligently. You can answer the user questions directly using your own knowledge and information from earlier conversation messages or you can also use the tools provided to you to fetch data and information to answer the user questions more accurately.
#         ## Guidance:
#         1. If you are not able to answer the user question you can ask the user for more information or to elaborate the question.
#         2. If the tool returns incorrect or unsatisfying answer for the user question, or if the tools returns any error. You can try calling the tools again and then return the final answer. Strictly do not call the tool for more than three times to answer the same user question if the tool still returns similar answer.
#         '''


# summary_message = f'''
#                 ## Summary of the earlier conversation :
#                 {summary}
#                 '''

'''
import json
import re
from uuid import uuid4
from typing import Literal
from langchain_core.tools import tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

class State(MessagesState):
    summary: str
    response_type : Literal["search", "query"]

class ChatAgent:
    def __init__(self, llm):
        self.memory = MemorySaver()
        self.max_msgs = 10
        self.use_summarization = False
        self.llm = llm

        self.tools_dict = {"sql_tool" : sql_tool, "retriever_tool" : retriever_tool}
        self.tools = list(self.tools_dict.values())
        self.llm_with_tools = llm.bind_tools(self.tools)

        self.agent = self._create_agent()

        
    def _call_model(self, state: State):
        summary = state.get("summary", "")
        if summary:
            
            system_message = self.sys_prompt + summary_message
            messages = [SystemMessage(content=system_message)] + state["messages"]
        else:
            messages = [SystemMessage(content=self.sys_prompt)] + state["messages"]

        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _call_tool(self, state: State):
        messages = state["messages"]
        try:
            tool_call = messages[-1].tool_calls[0]
        except:
            tool_call = self._extract_tool_info(messages[-1].content)

        try:
            tool = self.tools_dict[tool_call["name"]]
            tool_output, tool_artifact = tool.invoke(tool_call["args"])

        except:
            tool_output = "Error occured when calling the tool. Please provide correct input for the tool"
            tool_artifact = []

        tool_response = ToolMessage(content=tool_output, artifact=tool_artifact, tool_call_id=tool_call["id"])
        return {"messages" : [tool_response]}

    def _should_continue(self, state: State):
        messages = state["messages"]
        if messages[-1].tool_calls:
            return "call_tools"

        pattern = r"<function=(\w+)(\{.*?\})</function>"
        match = re.search(pattern, messages[-1].content)
        if match:
            return "call_tools"

        if len(messages) > self.max_msgs:
            return "manage_conversation_len"

        return END

    def _return_response(self, state: State):
        messages = state["messages"]
        response_type = state["response_type"]

        if response_type == "query":
            return "call_model"

        if len(messages) > self.max_msgs:
            return "manage_conversation_len"

        return END

    def _manage_conversation_len(self, state: State):
        if self.use_summarization :
            #use summarization
            summary = state.get("summary", "")
            if summary:
                summary_message = (
                    f"This is summary of the conversation to date: {summary}\n\n"
                    "Extend the summary by taking into account the new messages above:"
                )
            else:
                summary_message = "Create a summary of the conversation above:"

            messages = state["messages"] + [HumanMessage(content=summary_message)]
            response = self.llm.invoke(messages)

            delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
            return {"summary": response.content, "messages": delete_messages}

        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        return {"messages": delete_messages}

    def _extract_tool_info(self, response):
        pattern = r"<function=(\w+)(\{.*?\})</function>"
        match = re.search(pattern, response)
        if match:
            tool_name = match.group(1)
            tool_args = json.loads(match.group(2))
            return {"name": tool_name, "args": tool_args, "id": str(uuid4())[:8]}
        return None

    def _create_agent(self):
        workflow = StateGraph(State)

        workflow.add_node("call_model", self._call_model)
        workflow.add_node("manage_conversation_len", self._manage_conversation_len)
        workflow.add_node("call_tools", self._call_tool)

        workflow.add_edge(START, "call_model")
        workflow.add_conditional_edges("call_model", self._should_continue)
        workflow.add_conditional_edges("call_tools", self._return_response)
        workflow.add_edge("manage_conversation_len", END)

        agent = workflow.compile(checkpointer=self.memory)
        return agent

    def get_response(self, query, response_type, session_id):
        config = {"configurable": {"thread_id": f"{session_id}"}}

        user_message = HumanMessage(content= query.strip())
        response = self.agent.invoke({"messages": [user_message], "response_type" : response_type}, config)

        if response_type == "query":
            return response["messages"][-1].content, response
        try:
            return response["messages"][-1].artifact, response
        except:
           return [{"response" : response["messages"][-1].content}], response

    def clear_chat(self, session_id):
        state = self.agent.get_state(config={"configurable": {"thread_id": f"{session_id}"}})
        messages = state.values["messages"]
        delete_messages = [RemoveMessage(id=m.id) for m in messages[:]]
        self.agent.update_state(values={"messages" : delete_messages}, config={"configurable": {"thread_id": f"{session_id}"}}, as_node="manage_conversation_len")

        return {"message" : "Successfully cleared chat history."}

#Define Tools
from app.services.chat.sql_tool import sql_tool_func
from app.services.chat.retriever_tool import retriever_tool_func
# '''
# @tool
# def sql_tool(user_query : str):
#     """
#     Fetch data from the PostgreSQL Database and returns data to answer the user query.

#     Args:
#         user_query (str) : concise and clear information about the question asked by the user

#     Returns:
#         Response (str) : The data fetched from the database or an error message if any error occurred.
#     """

#     tool_output, tool_artifact = sql_tool_func(user_query)

#     return tool_output, tool_artifact

# @tool
# def retriever_tool(user_query : str):
#     """
#     Search and retrieve the most relevant documents and information from vector database based on their semantic similarity to the user query.

#     Args:
#         user_query (str) : concise and clear information about the question asked by the user

#     Returns:
#         Response (str) : Text containing the information fetched from the vector database or an error message if any error occurred.
#     """
#     tool_output, tool_artifact = retriever_tool_func(user_query)

#     return tool_output, tool_artifact



