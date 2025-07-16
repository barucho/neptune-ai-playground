import argparse
import os
from strands import Agent
from strands.tools.mcp import MCPClient
from strands_tools import file_read, file_write
from mcp import StdioServerParameters, stdio_client
from dotenv import load_dotenv
from strands.models import BedrockModel


load_dotenv()

# Bedrock
bedrock_model = BedrockModel(
    model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    region_name='us-east-1',
    temperature=0.3,
)

def get_environment_variables():
    """Get environment variables with defaults and error handling."""
    # Get cluster endpoint (required)
    cluster_endpoint = os.getenv("CLUSTER_ENDPOINT")
    print(cluster_endpoint)
    if not cluster_endpoint:
        raise ValueError(
            "Error: CLUSTER_ENDPOINT environment variable is not set.\n"
            "Please set it using .env file")
    return {
        "cluster_endpoint": cluster_endpoint
    }


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Neptune client using strands Agent")
    parser.add_argument("prompt", help="Prompt to send to the agent")

    # Parse arguments
    args = parser.parse_args()

    # Get environment variables with defaults and error handling
    env_vars = get_environment_variables()
    mcp_args = [
        "awslabs.amazon-neptune-mcp-server@latest"
    ]

    mcp_env = { "FASTMCP_LOG_LEVEL": "INFO", "NEPTUNE_ENDPOINT":"neptune-db://"+env_vars["cluster_endpoint"] }
    
    # Create the DSQL MCP client with NPX, the cluster name, and the AWS region
    dsql_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx", args=mcp_args, env=mcp_env
                )
            )
        )

    # Execute the prompt
    with dsql_client:
        tools = dsql_client.list_tools_sync()
        tools.extend([file_read, file_write])
        agent = Agent(model=bedrock_model,tools=tools)
        try:
            response = agent(args.prompt)
            print(response)
        except Exception as e:
            print(f"Error executing prompt: {e}")


if __name__ == "__main__":
    main()
