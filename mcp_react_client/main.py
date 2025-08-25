"""
MCP ReAct Client - A ReAct-based client for MCP servers using LangChain

This client connects to an MCP Python interpreter server and allows users to interact
with Python environments through natural language commands.
"""

import asyncio
import os
import logging
from typing import List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters, stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import tool
from .image_generator import generate_single_image, generate_comic


@tool
def create_image(prompt: str, filename: str = None, size: str = "1024x1024", quality: str = "standard") -> str:
    """
    Create an image using OpenAI DALL-E based on a text prompt.
    
    Args:
        prompt: Description of the image to generate
        filename: Optional filename for the saved image (defaults to auto-generated)
        size: Image size (1024x1024, 1792x1024, or 1024x1792)
        quality: Image quality (standard or hd)
    
    Returns:
        Path to the saved image file
    """
    try:
        return generate_single_image(prompt, filename, size, quality)
    except Exception as e:
        return f"Error generating image: {str(e)}"


@tool
def create_comic(topic: str) -> str:
    """
    Create a 4-panel comic based on a topic using OpenAI DALL-E.
    
    Args:
        topic: Topic or theme for the comic story
    
    Returns:
        Path to the generated comic image file
    """
    try:
        return generate_comic(topic)
    except Exception as e:
        return f"Error generating comic: {str(e)}"


async def load_all_tools(session):
    """Load both MCP tools and image generation tools"""
    # Load MCP tools
    mcp_tools = await load_mcp_tools(session)
    
    # Add image generation tools
    image_tools = [create_image, create_comic]
    
    # Combine all tools
    all_tools = mcp_tools + image_tools
    
    return all_tools


def setup_logging(verbose=False):
    """Set up logging configuration for debugging ReAct agent."""
    if verbose:
        # Set up minimal logging - only show errors from other components
        logging.basicConfig(
            level=logging.ERROR,
            format='%(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()],
            force=True
        )
        
        # Suppress noisy loggers
        logging.getLogger("openai").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("httpcore").setLevel(logging.ERROR)
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        logging.getLogger("langchain").setLevel(logging.ERROR)
        logging.getLogger("langchain_core").setLevel(logging.ERROR)
        logging.getLogger("langgraph").setLevel(logging.ERROR)
        logging.getLogger("mcp").setLevel(logging.ERROR)
        logging.getLogger("langchain_mcp_adapters").setLevel(logging.ERROR)
    else:
        # Normal mode - suppress all debug logs
        logging.basicConfig(level=logging.WARNING, force=True)


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
        ]),
        ("Image Generation", [
            "Create an image of a sunset over mountains",
            "Generate a 4-panel comic about artificial intelligence",
            "Create a beautiful landscape with trees and rivers"
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


async def interactive_mode(verbose=False):
    """Run the MCP ReAct client in interactive mode."""
    
    print("🚀 Starting MCP ReAct Client - Interactive Mode")
    if verbose:
        print("🔍 Verbose mode enabled - detailed logging active")
    print("=" * 50)
    print("💡 Type your commands and press Enter. Type 'quit', 'exit', or 'q' to stop.")
    print("=" * 50)
    
    # Setup logging
    setup_logging(verbose)
    
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
                
                # Get all tools (MCP + image generation)
                tools = await load_all_tools(session)
                
                print(f"✅ Loaded {len(tools)} tools from MCP server")
                print("\n📚 Available tools:")
                for tool in tools:
                    print(f"  • {tool.name}")
                
                print("\n💡 Special commands:")
                print("  • 'help' - Show example commands")
                print("  • 'tools' - List all available tools")
                print("  • 'verbose' - Toggle verbose logging on/off")
                print("  • 'quit', 'exit', 'q' - Exit the program")
                
                print("\n" + "=" * 50)
                print("🎯 Ready for your commands!")
                
                # Interactive loop
                verbose_mode = verbose
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
                        elif user_input.lower() == 'verbose':
                            verbose_mode = not verbose_mode
                            setup_logging(verbose_mode)
                            status = "enabled" if verbose_mode else "disabled"
                            print(f"🔍 Verbose logging {status}")
                            continue
                        
                        print("\n" + "-" * 60)
                        print(f"Processing: {user_input}")
                        print("-" * 60)
                        
                        # Run the agent with user input
                        await run_react_agent(tools, user_input, verbose=verbose_mode)
                        
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


async def demo_mode(verbose=False):
    """Run the MCP ReAct client in demo mode with predefined queries."""
    
    print("🚀 Starting MCP ReAct Client - Demo Mode")
    if verbose:
        print("🔍 Verbose mode enabled - detailed logging active")
    print("=" * 50)
    
    # Setup logging
    setup_logging(verbose)
    
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
                
                # Get all tools (MCP + image generation)
                tools = await load_all_tools(session)
                
                print(f"Loaded {len(tools)} tools from MCP server:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Run each test query within the same session
                for i, query in enumerate(test_queries, 1):
                    print(f"\n{'='*20} Demo {i} {'='*20}")
                    await run_react_agent(tools, query, verbose=verbose)
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
    
    # Parse command line arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    # Remove verbose flags from argv for mode parsing
    clean_argv = [arg for arg in sys.argv if arg not in ["--verbose", "-v"]]
    
    # Check command line arguments
    if len(clean_argv) > 1:
        mode = clean_argv[1].lower()
        if mode == "demo":
            await demo_mode(verbose=verbose)
            return
        elif mode == "interactive":
            await interactive_mode(verbose=verbose)
            return
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Usage: python -m mcp_react_client.main [interactive|demo] [--verbose|-v]")
            return
    
    # Default to interactive mode
    await interactive_mode(verbose=verbose)


async def run_react_agent(tools: List, query: str, verbose=False):
    """Run the ReAct agent with the given query."""
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it using: export OPENAI_API_KEY='your-api-key'") 
    
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
    
    if verbose:
        print("\n🔍 REACT AGENT TOOL TRACE:")
        print("=" * 50)
        print(f"🎯 Query: {query}")
        print(f"🛠️  Available tools: {[tool.name for tool in tools]}")
        print("=" * 50)
    
    try:
        # Run the agent
        response = await agent.ainvoke({"messages": [("user", query)]})
        
        if verbose:
            print("\n📋 TOOL CALL SUMMARY:")
            print("-" * 30)
            tool_call_count = 0
            
            if response and "messages" in response:
                # Show only tool-related interactions
                for i, msg in enumerate(response["messages"]):
                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        tool_call_count += len(msg.tool_calls)
                        print(f"\n🤖 Agent Decision #{i//2 + 1}:")
                        for j, tool_call in enumerate(msg.tool_calls, 1):
                            tool_name = tool_call.get('function', {}).get('name', tool_call.get('name', 'unknown'))
                            print(f"  {j}. 🔧 Tool: {tool_name}")
                            
                            # Show simplified args
                            args = tool_call.get('function', {}).get('arguments')
                            if args and isinstance(args, str):
                                try:
                                    import json
                                    parsed_args = json.loads(args)
                                    # Show only key parameters
                                    key_params = {}
                                    for key, value in parsed_args.items():
                                        if key in ['file_path', 'code', 'package_name', 'environment']:
                                            if isinstance(value, str) and len(value) > 50:
                                                key_params[key] = value[:50] + "..."
                                            else:
                                                key_params[key] = value
                                    if key_params:
                                        print(f"     📝 Key params: {key_params}")
                                except:
                                    pass
                    
                    # Show tool results
                    elif hasattr(msg, 'content') and hasattr(msg, 'role') and getattr(msg, 'role', None) == 'tool':
                        result_preview = str(msg.content)[:100] + "..." if len(str(msg.content)) > 100 else str(msg.content)
                        print(f"  ✅ Tool result: {result_preview}")
                
                print(f"\n📊 Total tool calls executed: {tool_call_count}")
            print("-" * 30)
        
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
        if verbose:
            import traceback
            print("\n🔍 FULL ERROR TRACEBACK:")
            traceback.print_exc()
        return None
    
    return response


def cli_main():
    """Command line interface main function."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
