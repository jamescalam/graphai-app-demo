import json

import openai
from graphai import Graph, node, router
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from .tools import search_web_tool
from .utils.logger import logger


class FinalAnswer(BaseModel):
    answer: str = Field(description="The final answer to the question")
    sources: list[str] = Field(description="The sources used to answer the question")

final_answer_schema = openai.pydantic_function_tool(FinalAnswer)
final_answer_schema["function"]["name"] = "final_answer"  # align with node name

class SearchWeb(BaseModel):
    def __name__(self):
        return "search_web"

    query: str = Field(description="The query to search the web for")

search_web_schema = openai.pydantic_function_tool(SearchWeb)
search_web_schema["function"]["name"] = "search_web"  # align with node name

client = AsyncOpenAI()

@node(start=True)
async def node_start(input: dict) -> dict[str, str]:
    logger.info(f"node_start({input=})")
    return {"query": input["query"]}

#@node(tool=SearchWeb)  # TODO could this be useful?
@node(stream=True)
async def search_web(input: str, callback) -> dict[str, dict]:
    logger.info(f"search_web({input=})")
    out = await search_web_tool(input)
    callback(out)
    return {
        "input": {
            "text": out,
            **input
        }
    }

@node(end=True)
async def final_answer(input: dict[str, str]) -> dict[str, str]:
    logger.info(f"final_answer({input=})")
    return {
        "answer": str(input.get("text", "No answer available")),
        "sources": "No sources found"
    }

# this is our central LLM node
@router(stream=True)
async def llm_node(input: dict, callback):
    logger.info(f"llm_node({input=})")
    chat_history = [
        {"role": message["role"], "content": message["content"]}
        for message in input["chat_history"]
    ]
    # construct all messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        *chat_history,
        {"role": "user", "content": input["query"]},
    ]
    if input.get("text"):
        messages.append({"role": "user", "content": (
            f"Respond to the following query from the user: {input['query']}"
            "Here is additional context. You can use it to answer the query. "
            f"But do not directly reference it: {input.get('text', '')}. "
            "If you have the information to answer the query, use the final_answer "
            "tool."
        )})
    print(f"{search_web_schema=}")
    # we stream directly from the client
    print(f"{messages=}")
    stream = await client.chat.completions.create(
        messages=messages,
        model="gpt-4o-mini",
        stream=True,
        tools=[
            search_web_schema,
            final_answer_schema
        ],
        tool_choice="required"
    )

    first_chunk = True  # first chunk contains the tool name
    args_str = ""
    async for chunk in stream:
        choice = chunk.choices[0]
        if first_chunk:
            toolname = choice.delta.tool_calls[0].function.name.lower()
            first_chunk = False
            callback("<graphai:toolname:" + toolname + ">")
        elif choice.finish_reason == "tool_calls":
            # this means we finished the tool call
            pass
        else:
            chunk_text = str(choice.delta.tool_calls[0].function.arguments)
            callback(chunk_text)
            args_str += chunk_text
    args = json.loads(args_str)
    output = {
        "choice": toolname,
        "input": {**input, **args}
    }
    print(output)
    return output


def create_graph():
    graph = Graph()

    for node_fn in [node_start, llm_node, search_web, final_answer]:
        print(node_fn.name)
        print(node_fn._func_signature)
        graph.add_node(node_fn)
    
    # add optional edges
    graph.add_router(
        sources=[node_start],
        router=llm_node,
        destinations=[search_web, final_answer]
    )

    graph.add_edge(node_start, llm_node)
    graph.add_edge(search_web, llm_node)

    return graph
