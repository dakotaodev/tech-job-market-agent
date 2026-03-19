from fastmcp import FastMCP

mcp = FastMCP(name="job-market-tools")

@mcp.tool()
def ping() -> str:
    return "pong"

if __name__=="__main__":
    mcp.run()