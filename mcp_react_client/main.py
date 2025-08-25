"""
MCP ReAct Client - A ReAct-based client for MCP servers using LangChain

This client connects to an MCP Python interpreter server and allows users to interact
with Python environments through natural language commands.
"""

import asyncio
import os
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters, stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools


def show_help():
    """Show help with example commands."""
    print("\n" + "=" * 60)
    print("📖 HELP - Example Commands")
    print("=" * 60)
    
    examples = [
        ("Python Environment Management", [
            "Show me all available Python environments",
            "List installed packages in default environment",
            "Install numpy package in system environment"
        ]),
        ("Python Code Execution", [
            "Run this Python code: print('Hello, World!')",
            "Execute this code: import math; print(math.pi)",
            "Run a calculation: 2 + 2 * 3"
        ]),
        ("File Operations", [
            "Create a Python file called 'test.py' with a hello function",
            "Read the contents of hello.py file",
            "List all files in the current directory"
        ]),
        ("Advanced Examples", [
            "Create a script that calculates fibonacci numbers",
            "Write a Python function to sort a list",
            "Run a data analysis script with pandas"
        ]),
        ("Complex Engineering Tasks", [
            "Optimize a hot-rolling steel process using Bayesian optimization",
            "Create a machine learning model for predictive maintenance",
            "Solve a multi-objective optimization problem with constraints"
        ])
    ]
    
    for category, commands in examples:
        print(f"\n🔸 {category}:")
        for cmd in commands:
            print(f"   • {cmd}")
    
    print("\n" + "=" * 60)


def show_tools(tools):
    """Show detailed information about available tools."""
    print("\n" + "=" * 60)
    print("🛠️  AVAILABLE TOOLS")
    print("=" * 60)
    
    for i, tool in enumerate(tools, 1):
        print(f"\n{i}. 🔧 {tool.name}")
        print(f"   📝 {tool.description}")
    
    print("\n" + "=" * 60)


async def interactive_mode():
    """Run the MCP ReAct client in interactive mode."""
    
    print("🚀 Starting MCP ReAct Client - Interactive Mode")
    print("=" * 50)
    print("💡 Type your commands and press Enter. Type 'quit', 'exit', or 'q' to stop.")
    print("=" * 50)
    
    # MCP server parameters from mcp.json configuration
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "mcp-python-code-interpreter",
            "--dir",
            "/Users/uengine/temp",
            "--python-path",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        ],
        env={"MCP_ALLOW_SYSTEM_ACCESS": "0"}
    )
    
    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools from the MCP server
                tools = await load_mcp_tools(session)
                
                print(f"✅ Loaded {len(tools)} tools from MCP server")
                print("\n📚 Available tools:")
                for tool in tools:
                    print(f"  • {tool.name}")
                
                print("\n💡 Special commands:")
                print("  • 'help' - Show example commands")
                print("  • 'tools' - List all available tools")
                print("  • 'quit', 'exit', 'q' - Exit the program")
                
                print("\n" + "=" * 50)
                print("🎯 Ready for your commands!")
                
                # Interactive loop
                while True:
                    try:
                        # Get user input
                        user_input = input("\n🤖 Enter your command: ").strip()
                        
                        # Check for exit commands
                        if user_input.lower() in ['quit', 'exit', 'q', '']:
                            print("👋 Goodbye!")
                            break
                        
                        # Handle special commands
                        if user_input.lower() == 'help':
                            show_help()
                            continue
                        elif user_input.lower() == 'tools':
                            show_tools(tools)
                            continue
                        
                        print("\n" + "-" * 60)
                        print(f"Processing: {user_input}")
                        print("-" * 60)
                        
                        # Run the agent with user input
                        await run_react_agent(tools, user_input)
                        
                        print("\n" + "=" * 60)
                        
                    except KeyboardInterrupt:
                        print("\n\n👋 Interrupted by user. Goodbye!")
                        break
                    except EOFError:
                        print("\n\n👋 EOF detected. Goodbye!")
                        break
                    except Exception as e:
                        print(f"\n❌ Error processing command: {e}")
                        print("Please try again or type 'quit' to exit.")
                        
    except Exception as e:
        print(f"❌ Failed to set up MCP client: {e}")
        print("Make sure the MCP Python interpreter server is available.")
        return


async def demo_mode():
    """Run the MCP ReAct client in demo mode with predefined queries."""
    
    print("🚀 Starting MCP ReAct Client - Demo Mode")
    print("=" * 50)
    
    # MCP server parameters from mcp.json configuration
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "mcp-python-code-interpreter",
            "--dir",
            "/Users/uengine/temp",
            "--python-path",
            "/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
        ],
        env={"MCP_ALLOW_SYSTEM_ACCESS": "0"}
    )
    
    # Test queries
    test_queries = [
        "Show me all available Python environments on my system",
        "Run this Python code: print('Hello, world!')",
        "Create a new Python file called 'hello.py' with a function that says hello"
    ]
    
    try:
        # Connect to the MCP server
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools from the MCP server
                tools = await load_mcp_tools(session)
                
                print(f"Loaded {len(tools)} tools from MCP server:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Run each test query within the same session
                for i, query in enumerate(test_queries, 1):
                    print(f"\n{'='*20} Demo {i} {'='*20}")
                    await run_react_agent(tools, query)
                    print("\n" + "="*50)
                    
                    # Add a small delay between queries
                    await asyncio.sleep(2)
                    
    except Exception as e:
        print(f"❌ Failed to set up MCP client: {e}")
        print("Make sure the MCP Python interpreter server is available.")
        return
    
    print("\n✅ All demos completed!")


async def main():
    """Main function to run the MCP ReAct client."""
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "demo":
            await demo_mode()
            return
        elif mode == "interactive":
            await interactive_mode()
            return
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Usage: python -m mcp_react_client.main [interactive|demo]")
            return
    
    # Default to interactive mode
    await interactive_mode()


async def run_react_agent(tools: List, query: str):
    """Run the ReAct agent with the given query."""
    
    # Load environment variables
    load_dotenv()
    
    # Set OpenAI API key directly if not in environment
    openai_api_key = os.getenv("OPENAI_API_KEY") 
    
    # Set up the OpenAI model
    model = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=openai_api_key
    )
    
    # Create the ReAct agent
    agent = create_react_agent(model, tools)
    
    print(f"\n🤖 Processing query: {query}")
    print("-" * 50)
    
    try:
        # Run the agent
        response = await agent.ainvoke({"messages": [("user", query)]})
        
        print("\n📋 Agent Response:")
        print("-" * 20)
        
        # Print the final message from the agent
        if response and "messages" in response:
            final_message = response["messages"][-1]
            if hasattr(final_message, 'content'):
                print(final_message.content)
            else:
                print(final_message)
        else:
            print(response)
            
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    return response


def cli_main():
    """Command line interface main function."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
