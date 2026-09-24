import os
import json
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Annotated, List, Optional, Union, Dict, Any, Literal

from sse_starlette.sse import EventSourceResponse, ServerSentEvent
from fastapi.middleware.cors import CORSMiddleware

from app.agent import build_graph
from app.config import load_settings

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_settings()
    get_graph()
    yield


app = FastAPI(title="Portfolio API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGIN", "http://localhost:5173").split(";"),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextContent(BaseModel):
    type: Literal["text"] = "text"
    text: str

class ImageUrl(BaseModel):
    url: str
    detail: Optional[Literal["auto", "low", "high"]] = "auto"

class ImageContent(BaseModel):
    type: Literal["image_url"] = "image_url"
    image_url: ImageUrl

MessageContent = Annotated[
    Union[TextContent, ImageContent], Field(discriminator="type")
]

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Union[str, list[MessageContent]]
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None

class CompletionRequest(BaseModel):
    model: str
    prompt: Union[str, List[str]]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponseChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: Usage

class CompletionResponseChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class CompletionResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionResponseChoice]
    usage: Usage

class DeltaMessage(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None

class ChatCompletionStreamResponseChoice(BaseModel):
    index: int
    delta: DeltaMessage
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatCompletionStreamResponseChoice]

class CompletionStreamResponseChoice(BaseModel):
    text: str
    index: int
    logprobs: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None

class CompletionStreamResponse(BaseModel):
    id: str
    object: str = "text_completion"
    created: int
    model: str
    choices: List[CompletionStreamResponseChoice]

async def call_llm_api(prompt: Union[str, List[ChatMessage]], **kwargs) -> str:
    """
    Call the LangGraph agent non-streaming.
    """
    last_msg = prompt if isinstance(prompt, str) else prompt[-1].content
    if isinstance(last_msg, list):
        question = "".join(part.text for part in last_msg if getattr(part, "type", "") == "text")
    else:
        question = last_msg

    state = await get_graph().ainvoke({"question": question})

    return state["final_answer"]

async def stream_llm_api(prompt: Union[str, List[ChatMessage]], **kwargs):
    """
    Stream only the saujana_node response token by token using LangGraph astream_events.
    """
    last_msg = prompt if isinstance(prompt, str) else prompt[-1].content
    if isinstance(last_msg, list):
        question = "".join(part.text for part in last_msg if getattr(part, "type", "") == "text")
    else:
        question = last_msg

    graph = get_graph()

    streamed_any = False
    final_fallback_answer = None

    async for event in graph.astream_events({"question": question}, version="v2"):
        event_name = event.get("event")
        node_name = event.get("metadata", {}).get("langgraph_node")

        if event_name == "on_chat_model_stream" and node_name == "saujana":
            chunk = event["data"]["chunk"]
            if chunk.content:
                streamed_any = True
                yield chunk.content

        elif event_name == "on_chain_end" and node_name in ("gatekeeper", "saujana"):
            output = event.get("data", {}).get("output")
            if isinstance(output, dict) and output.get("final_answer"):
                final_fallback_answer = output["final_answer"]

    if not streamed_any and final_fallback_answer:
        yield final_fallback_answer

@app.post("/api/v1/chat/completions", response_model=Union[ChatCompletionResponse, ChatCompletionStreamResponse])
async def create_chat_completion(request: ChatCompletionRequest):
    if request.stream:
        async def generate_stream():
            stream_id = f"chatcmpl-{int(time.time() * 1000)}"
            created = int(time.time())

            async for chunk in stream_llm_api(
                request.messages,
                **request.model_dump(exclude={"messages", "stream"})
            ):
                response = ChatCompletionStreamResponse(
                    id=stream_id,
                    created=created,
                    model=request.model,
                    choices=[
                        ChatCompletionStreamResponseChoice(
                            index=0,
                            delta=DeltaMessage(content=chunk),
                            finish_reason=None,
                        )
                    ],
                )

                yield ServerSentEvent(
                    data=response.model_dump_json()
                )

            # Final chunk
            final_response = {
                "id": stream_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": request.model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {},
                        "finish_reason": "stop",
                    }
                ],
            }

            yield ServerSentEvent(
                data=json.dumps(final_response)
            )

            # OpenAI-compatible stream terminator
            yield ServerSentEvent(data="[DONE]")

        return EventSourceResponse(generate_stream())
    
    response_text = await call_llm_api(request.messages, **request.model_dump(exclude={'messages'}))
    
    return ChatCompletionResponse(
        id=f"chatcmpl-{int(time.time()*1000)}",
        created=int(time.time()),
        model=request.model,
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatMessage(role="assistant", content=response_text),
                finish_reason="stop"
            )
        ],
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)  # Implement token counting as needed
    )

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
