"""
Chainlit Web UI for Gmail & Google Drive MCP Server
Provides a web interface to interact with the MCP server
Run with: chainlit run backend/chainlit_app.py
"""

# Chainlit framework for web UI
import chainlit as cl  # Main Chainlit library for building LLM UIs

# LangChain imports for LLM integration
from langchain_openai import ChatOpenAI  # OpenAI LLM
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # Message types
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # Prompts

# Standard library
import sys  # System utilities
import json  # JSON parsing
from pathlib import Path  # File operations

# Import tool handler from layered architecture
from handlers.tool_handler import get_handler

# Load environment
import os
from dotenv import load_dotenv
load_dotenv()


# ============================================================================
# TOOL DEFINITIONS FOR LLM
# ============================================================================

TOOLS_DESCRIPTION = """
You have access to the following tools for Gmail and Google Drive:

GMAIL TOOLS:
1. list_emails(query="is:unread", max_results=10)
   - Lists emails matching Gmail search query
   - Returns: JSON with email list (id, from, subject, date, snippet)

2. read_email(email_id="...")
   - Fetches complete email content
   - Returns: JSON with full email (body, headers, attachments info)

3. send_email(to="...", subject="...", body="...", cc="", bcc="")
   - Sends an email
   - Returns: JSON with success status and message ID

GOOGLE DRIVE TOOLS:
1. list_drive_files(query="", max_results=10, file_type="")
   - Lists files in Google Drive
   - Returns: JSON with file list (name, size, type, link)

2. get_file_info(file_id="...")
   - Gets detailed file information
   - Returns: JSON with file metadata (owner, permissions, etc.)

3. search_drive(keyword="...", max_results=20)
   - Searches Drive by keyword
   - Returns: JSON with search results

When the user asks you to interact with Gmail or Drive, use these tools to help them.
Always parse the JSON responses and present them in a readable format to the user.
"""


# ============================================================================
# TOOL EXECUTION
# ============================================================================

async def execute_tool(tool_name: str, **kwargs) -> str:
    """
    Execute a tool using ToolHandler and return the result.
    
    Args:
        tool_name: Name of the tool to execute
        **kwargs: Tool arguments
    
    Returns:
        Tool execution result as JSON string
    """
    try:
        handler = get_handler("chainlit-user")
        
        # Route to appropriate tool via ToolHandler
        if tool_name == "list_emails":
            return handler.list_emails(
                query=kwargs.get("query", "is:unread"),
                max_results=int(kwargs.get("max_results", 10))
            )
        
        elif tool_name == "read_email":
            return handler.read_email(email_id=kwargs.get("email_id"))
        
        elif tool_name == "send_email":
            return handler.send_email(
                to=kwargs.get("to"),
                subject=kwargs.get("subject"),
                body=kwargs.get("body"),
                cc=kwargs.get("cc"),
                bcc=kwargs.get("bcc")
            )
        
        elif tool_name == "list_drive_files":
            return handler.list_drive_files(
                query=kwargs.get("query", ""),
                max_results=int(kwargs.get("max_results", 10)),
                file_type=kwargs.get("file_type", "")
            )
        
        elif tool_name == "get_file_info":
            return handler.get_file_info(file_id=kwargs.get("file_id"))
        
        elif tool_name == "search_drive":
            return handler.search_drive(
                keyword=kwargs.get("keyword"),
                max_results=int(kwargs.get("max_results", 20))
            )
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            })
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        })


# ============================================================================
# CHAINLIT INTERFACE
# ============================================================================

@cl.on_chat_start
async def start():
    """
    Initialize chat session with system message.
    Called when user starts a new conversation.
    """
    system_message = f"""You are a helpful Gmail and Google Drive assistant.
{TOOLS_DESCRIPTION}

When the user asks you to do something with their email or files:
1. Use the appropriate tool to fetch the information
2. Present the results in a clear, readable format
3. Ask follow-up questions if needed
4. Always be respectful of the user's data

If a tool returns an error, explain it to the user and suggest solutions."""
    
    cl.user_session.set("system_message", system_message)
    
    await cl.Message(
        content="👋 Welcome to Gmail & Google Drive Assistant!\n\n"
                "I can help you:\n"
                "- 📧 List, read, and send emails\n"
                "- 📁 Browse and search Google Drive\n"
                "- 📊 Get file information and details\n\n"
                "What would you like to do?"
    ).send()


async def main(message: cl.Message):
    """
    Process user messages and interact with tools.
    
    Args:
        message: User's message
    """
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
    )
    
    system_message = cl.user_session.get("system_message")
    chat_history = cl.user_session.get("chat_history", [])
    
    messages = [
        SystemMessage(content=system_message),
        *chat_history,
        HumanMessage(content=message.content)
    ]
    
    thinking_msg = cl.Message(content="🤔 Processing your request...")
    await thinking_msg.send()
    
    try:
        response = llm.invoke(messages)
        await thinking_msg.remove()
        
        response_text = response.content
        
        tool_calls = []
        if "[TOOL:" in response_text:
            import re
            matches = re.findall(r'\[TOOL:(\w+)\((.*?)\)\]', response_text)
            for tool_name, args_str in matches:
                try:
                    args = eval(f"dict({args_str})")
                    tool_calls.append((tool_name, args))
                except:
                    pass
        
        if tool_calls:
            tool_results = []
            for tool_name, args in tool_calls:
                result = await execute_tool(tool_name, **args)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
            
            if tool_results:
                response_text += "\n\n📊 **Results:**\n"
                for tool_result in tool_results:
                    response_text += f"- {tool_result['tool']}: "
                    try:
                        result_obj = json.loads(tool_result['result'])
                        if result_obj.get('success'):
                            response_text += "✅ Success\n"
                        else:
                            response_text += f"❌ {result_obj.get('error', 'Unknown error')}\n"
                    except:
                        response_text += tool_result['result'] + "\n"
        
        await cl.Message(content=response_text).send()
        
        chat_history.append(HumanMessage(content=message.content))
        chat_history.append(AIMessage(content=response_text))
        cl.user_session.set("chat_history", chat_history)
    
    except Exception as e:
        await thinking_msg.remove()
        await cl.Message(
            content=f"❌ Error: {str(e)}\n\nPlease check that:\n"
                   "- credential.json is in the backend folder\n"
                   "- Google APIs are enabled\n"
                   "- Environment is properly configured"
        ).send()


async def handle_tool_request(message: cl.Message):
    """
    Handle direct tool requests in natural language.
    
    Format: /tool tool_name arg1=value1 arg2=value2
    """
    if message.content.startswith("/tool"):
        parts = message.content[5:].strip().split()
        
        if not parts:
            await cl.Message(content="❌ Usage: /tool tool_name arg1=value1 arg2=value2").send()
            return
        
        tool_name = parts[0]
        kwargs = {}
        
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                value = value.strip('"\'')
                kwargs[key] = value
        
        result = await execute_tool(tool_name, **kwargs)
        
        try:
            result_obj = json.loads(result)
            result_text = json.dumps(result_obj, indent=2)
        except:
            result_text = result
        
        await cl.Message(content=f"**Tool:** {tool_name}\n```json\n{result_text}\n```").send()


@cl.on_message
async def route_message(message: cl.Message):
    """
    Route messages to appropriate handler.
    """
    if message.content.startswith("/"):
        await handle_tool_request(message)
    else:
        await main(message)


if __name__ == "__main__":
    print("🚀 Starting Chainlit web UI...")
    print("Open http://localhost:8000 in your browser")
