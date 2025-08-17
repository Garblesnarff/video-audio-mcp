from mcp.server.fastmcp import FastMCP
from mcp_tools import ALL_TOOLS

# Create an MCP server instance
mcp = FastMCP("VideoAudioServer")

# Add a simple health_check tool
@mcp.tool()
def health_check() -> str:
    """Returns a simple health status to confirm the server is running."""
    return "Server is healthy!"

# Register all the tools from the mcp_tools package
for tool in ALL_TOOLS:
    mcp.tool()(tool)

# Main execution block to run the server
if __name__ == "__main__":
    mcp.run()