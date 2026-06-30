"""MCP client using the official mcp library."""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPClient:
    def __init__(self, problem_id: str, model: Optional[str] = None):
        self.problem_id = problem_id
        self.model = model
        self._session: Optional[ClientSession] = None
        self._stdio_ctx = None
        self._session_ctx = None

        from openai import AsyncOpenAI

        if model and model.startswith("glm"):
            self.client = AsyncOpenAI(
                api_key=os.environ.get("GLM_API_KEY"),
                base_url="https://open.bigmodel.cn/api/paas/v4/",
            )
        else:
            self.client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    def is_openai_model(self, model: str) -> bool:
        return (
            model.startswith(("gpt-3.5", "gpt-4", "gpt-5", "o1", "o1-", "o3", "o3-", "o4", "o4-", "chatgpt-", "glm-"))
            or "/" in model
        )

    async def connect_to_server(self):
        server_cmd = (
            "import sys; sys.path.insert(0, 'src'); "
            "from scone_bench.server import main; main()"
        )
        params = StdioServerParameters(
            command="python",
            args=["-c", server_cmd],
            cwd=str(Path(__file__).parent.parent),
        )

        self._stdio_ctx = stdio_client(params)
        streams = await self._stdio_ctx.__aenter__()
        read_stream, write_stream = streams

        self._session_ctx = ClientSession(read_stream, write_stream)
        self._session = await self._session_ctx.__aenter__()
        await self._session.initialize()

    async def get_prompt(self) -> list:
        result = await self._session.call_tool(
            "setup_problem",
            {"problem_id": self.problem_id},
        )
        content = result.content
        return [type("TextContent", (), {"text": c.text})() for c in content if hasattr(c, "text")]

    async def get_tools(self) -> list[dict]:
        result = await self._session.list_tools()
        excluded = {"setup_problem", "grade_problem"}
        return [
            self._to_api_tool(t)
            for t in result.tools
            if t.name not in excluded
        ]

    def _to_api_tool(self, tool) -> dict:
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.inputSchema or {},
            },
        }

    async def execute_tool(self, tool_name: str, tool_args: dict) -> object:
        if tool_name == "grade_problem" and "transcript" in tool_args:
            if isinstance(tool_args["transcript"], list):
                tool_args = dict(tool_args)
                tool_args["transcript"] = json.dumps(tool_args["transcript"])

        try:
            result = await self._session.call_tool(tool_name, tool_args)
            return type("ToolResult", (), {
                "isError": getattr(result, "isError", False),
                "content": result.content,
            })()
        except Exception as e:
            return type("ToolResult", (), {
                "isError": True,
                "content": [type("TextContent", (), {"text": str(e)})()],
            })()

    async def cleanup(self):
        if self._session_ctx:
            try:
                await self._session_ctx.__aexit__(None, None, None)
            except Exception:
                pass
            self._session_ctx = None
        if self._stdio_ctx:
            try:
                await self._stdio_ctx.__aexit__(None, None, None)
            except Exception:
                pass
            self._stdio_ctx = None
        self._session = None
