from llama_hub.tools.google_search.base import GoogleSearchToolSpec
from llama_index.tools.tool_spec.load_and_search.base import LoadAndSearchToolSpec
from app.helpers import config_reader
from typing import List
from llama_index.tools.function_tool import FunctionTool

# Define config parameters
config = config_reader()
api_key = config.get("google", "api_key")
engine = config.get("google", "engine")

class GoogleSearch:
    def __init__(self) -> None:
        self.api_key = api_key
        self.engine = engine
        self.num = 5

    def stack(self) -> (List[FunctionTool], List[FunctionTool]):
        '''
        Stack the GoogleSearch tool and LoadAndSearch tool.
        Returns:
            (List[FunctionTool], List[FunctionTool]): GoogleSearch and LoadAndSearch tools.
        '''
        gsearch_tools = GoogleSearchToolSpec(key=self.api_key, engine=self.engine, num=self.num).to_tool_list()
        gsearch_load_and_search_tools = LoadAndSearchToolSpec.from_defaults(gsearch_tools[0]).to_tool_list()
        return gsearch_tools, gsearch_load_and_search_tools
  
