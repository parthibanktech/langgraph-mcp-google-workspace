"""
LangGraph Integration Example: Gmail & Google Drive Agent
Shows how to integrate the MCP server with LangGraph for AI agents
"""

# Type hints for better code clarity
from typing import Any, TypedDict, Annotated  # Type definitions for function parameters

# LangGraph imports for agent orchestration
from langgraph.graph import StateGraph, END  # Graph builder for agent workflow
from langgraph.graph.message import add_messages  # Message management utility
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage  # LangChain message types

# LangChain imports for LLM integration
from langchain_openai import ChatOpenAI  # OpenAI LLM integration
from langchain_core.tools import tool  # Decorator for tool registration
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # Prompt templates

# Standard library imports
import json  # JSON parsing for tool results
import sys  # System utilities
from pathlib import Path  # File path handling
import os  # Environment variables

# Ensure UTF-8 output encoding for Windows console compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Direct package import using standard layered architecture
from handlers.tool_handler import get_handler


# ============================================================================
# DEFINE AGENT STATE
# ============================================================================

class AgentState(TypedDict):
    """
    State definition for the LangGraph agent.
    Tracks messages and conversation history.
    """
    messages: Annotated[list[BaseMessage], add_messages]  # List of messages in conversation


# ============================================================================
# WRAP MCP TOOLS FOR LANGCHAIN
# ============================================================================

# Note: These are wrappers that convert MCP tools to LangChain tools
# LangChain tools can be called by the LLM through tool_choice mechanism


@tool
def gmail_list_emails(query: str = "is:unread", max_results: int = 10) -> str:
    """
    List and search emails from Gmail inbox.
    
    Args:
        query: Gmail search query (e.g., "is:unread", "from:user@example.com")
        max_results: Maximum number of emails to return
    
    Returns:
        JSON string with list of emails (includes validation, rate limiting, audit logging)
    """
    # New layered architecture with validation + rate limiting + audit logging
    handler = get_handler("langgraph-user")
    return handler.list_emails(query=query, max_results=max_results)


@tool
def gmail_read_email(email_id: str) -> str:
    """
    Fetch complete email content by message ID.
    
    Args:
        email_id: Gmail message ID (from list_emails results)
    
    Returns:
        JSON string with complete email content (with validation + audit logging)
    """
    handler = get_handler("langgraph-user")
    return handler.read_email(email_id=email_id)


@tool
def gmail_send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """
    Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text
        cc: Carbon copy recipients (optional)
        bcc: Blind carbon copy recipients (optional)
    
    Returns:
        JSON string with success status and message ID (with full validation + logging)
    """
    handler = get_handler("langgraph-user")
    return handler.send_email(to=to, subject=subject, body=body, cc=cc, bcc=bcc)


@tool
def drive_list_files(query: str = "", max_results: int = 10, file_type: str = "") -> str:
    """
    List files in Google Drive with optional filtering.
    
    Args:
        query: Search query for files
        max_results: Maximum number of files to return
        file_type: Filter by MIME type (e.g., "application/vnd.google-apps.folder")
    
    Returns:
        JSON string with list of files and metadata (with validation + rate limiting)
    """
    handler = get_handler("langgraph-user")
    return handler.list_drive_files(query=query, max_results=max_results, file_type=file_type)


@tool
def drive_get_file_info(file_id: str) -> str:
    """
    Get detailed information about a Google Drive file.
    
    Args:
        file_id: Google Drive file ID
    
    Returns:
        JSON string with detailed file information (with validation + logging)
    """
    handler = get_handler("langgraph-user")
    return handler.get_file_info(file_id=file_id)


@tool
def drive_search(keyword: str, max_results: int = 20) -> str:
    """
    Search Google Drive by keyword.
    
    Args:
        keyword: Search keyword
        max_results: Maximum number of results
    
    Returns:
        JSON string with search results (with validation + audit logging)
    """
    handler = get_handler("langgraph-user")
    return handler.search_drive(keyword=keyword, max_results=max_results)


# ============================================================================
# AGENT TOOLS REGISTRY
# ============================================================================

# Register all tools for the agent
TOOLS = [
    gmail_list_emails,  # Gmail: List/search emails
    gmail_read_email,  # Gmail: Read email content
    gmail_send_email,  # Gmail: Send email
    drive_list_files,  # Drive: List files
    drive_get_file_info,  # Drive: Get file details
    drive_search,  # Drive: Search files
]

# Create tool names for reference
TOOL_NAMES = [tool.name for tool in TOOLS]


# ============================================================================
# INITIALIZE LLM WITH TOOLS
# ============================================================================

def create_agent():
    """
    Create and configure the LLM agent with tools.
    
    Returns:
        ChatOpenAI: Configured LLM instance with tool binding
    """
    # Initialize OpenAI LLM (uses OPENAI_API_KEY from environment)
    llm = ChatOpenAI(
        model="gpt-4",  # Use GPT-4 for better tool usage and reasoning
        temperature=0,  # Deterministic responses for tool use
    )
    
    # Bind tools to the LLM so it can call them
    llm_with_tools = llm.bind_tools(TOOLS)
    
    return llm_with_tools


# ============================================================================
# AGENT FUNCTIONS
# ============================================================================

def agent_node(state: AgentState, llm_with_tools):
    """
    Agent node: Processes messages and decides which tool to call.
    
    Args:
        state: Current agent state (messages)
        llm_with_tools: LLM with tool bindings
    
    Returns:
        Updated state with agent's response
    """
    # Get the latest message from conversation history
    messages = state["messages"]
    
    # Call LLM to get response and/or tool calls
    response = llm_with_tools.invoke(messages)
    
    # Return updated messages list with agent's response
    return {"messages": [response]}


def tool_node(state: AgentState):
    """
    Tool node: Executes the tools that the agent decides to use.
    
    Args:
        state: Current agent state (messages)
    
    Returns:
        Updated state with tool results
    """
    # Get the latest message (should be from agent with tool calls)
    messages = state["messages"]
    last_message = messages[-1]
    
    # Extract tool calls from the message
    tool_calls = last_message.tool_calls
    
    # Process each tool call
    tool_results = []
    for tool_call in tool_calls:
        # Find the tool by name
        tool = next((t for t in TOOLS if t.name == tool_call["name"]), None)
        
        if not tool:
            # Tool not found - create error message
            tool_result = f"Tool {tool_call['name']} not found"
        else:
            try:
                # Call the tool with its arguments
                result = tool.invoke(tool_call["args"])
                tool_result = result
            except Exception as e:
                # Handle tool execution errors
                tool_result = f"Error executing {tool_call['name']}: {str(e)}"
        
        # Create tool message with the result
        tool_message = ToolMessage(
            content=tool_result,
            tool_call_id=tool_call["id"],
            name=tool_call["name"],
        )
        tool_results.append(tool_message)
    
    # Return updated messages with tool results
    return {"messages": tool_results}


def should_continue(state: AgentState):
    """
    Routing logic: Decide whether to continue (call tool) or end.
    
    Args:
        state: Current agent state
    
    Returns:
        str: Next node ("tools" to execute tool, "end" to stop)
    """
    # Get the latest message from the agent
    messages = state["messages"]
    last_message = messages[-1]
    
    # Check if agent has tool calls
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"  # Call tools next
    else:
        return END  # No more tool calls, conversation is complete


# ============================================================================
# BUILD LANGGRAPH WORKFLOW
# ============================================================================

def create_graph():
    """
    Create and compile the LangGraph workflow.
    Defines the agent flow: user input -> agent -> tools -> response.
    
    Returns:
        Compiled LangGraph workflow
    """
    # Create the state graph
    workflow = StateGraph(AgentState)
    
    # Initialize LLM with tools
    llm_with_tools = create_agent()
    
    # Define nodes in the workflow
    workflow.add_node("agent", lambda state: agent_node(state, llm_with_tools))  # Agent decision node
    workflow.add_node("tools", tool_node)  # Tool execution node
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Define edges (routing logic)
    workflow.add_conditional_edges(
        "agent",  # From agent node
        should_continue,  # Use this function to decide next step
        {
            "tools": "tools",  # If tools needed, go to tools node
            END: END,  # If no tools, end the conversation
        }
    )
    
    # From tools node, always go back to agent
    workflow.add_edge("tools", "agent")
    
    # Compile the workflow into executable graph
    graph = workflow.compile()
    
    return graph


# ============================================================================
# RUN AGENT
# ============================================================================

def run_agent(user_input: str):
    """
    Run the agent with a user input.
    
    Args:
        user_input: User's query or instruction
    
    Example:
        run_agent("List my unread emails and send a reply to the first one")
    """
    # Create the workflow graph
    graph = create_graph()
    
    # Initialize agent state with user message
    initial_state = {
        "messages": [HumanMessage(content=user_input)]
    }
    
    # Run the agent
    print(f"🤖 User: {user_input}\n")
    
    # Execute the workflow
    result = graph.invoke(initial_state)
    
    # Extract and display the final response
    messages = result["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage):
        print(f"🤖 Agent: {last_message.content}")
    else:
        print(f"📊 Result: {last_message.content}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: List unread emails
    run_agent("What are my unread emails?")
    
    print("\n" + "="*60 + "\n")
    
    # Example 2: Search emails from a specific person
    run_agent("Show me recent emails from my manager")
    
    print("\n" + "="*60 + "\n")
    
    # Example 3: List Google Drive files
    run_agent("What files do I have in Google Drive?")
    
    print("\n" + "="*60 + "\n")
    
    # Example 4: Search Drive
    run_agent("Find my project documents in Google Drive")
