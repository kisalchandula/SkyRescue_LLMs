import asyncio
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional

from llama_index.core.base.llms.types import ChatMessage, ContentBlock
from llama_index.core.bridge.pydantic import BaseModel, Field, model_validator
from llama_index.core.memory.chat_memory_buffer import (
    DEFAULT_TOKEN_LIMIT,
    DEFAULT_CHAT_STORE_KEY
)
from llama_index.core.memory.types import BaseChatStoreMemory
from llama_index.core.prompts import BasePromptTemplate, RichPromptTemplate
from llama_index.core.utils import get_tokenizer

from workspace_agent import memory


class BaseMemoryBlock(BaseModel):

    name: str = Field(description="The name/identifier of the memory block.")
    description: Optional[str] = Field(default=None, description="A description of the memory block.")

    @abstractmethod
    def get(self, input: Optional[str] = None, **kwargs: Any) -> List[ContentBlock]:
        """Get the memory block."""
    
    async def aget(self, input: Optional[str] = None, **kwargs: Any) -> List[ContentBlock]:
        """Get the memory block (async)."""
        return await asyncio.to_thread(self.get, input, **kwargs)

    @abstractmethod
    def put(self, message: ChatMessage) -> None:
        """Put the memory block."""
    
    async def aput(self, message: ChatMessage) -> None:
        """Put the memory block (async)."""
        return await asyncio.to_thread(self.put, message)


class WaterfallMemory(BaseChatStoreMemory):

    token_limit: int = Field(default=DEFAULT_TOKEN_LIMIT)
    memory_blocks: List[BaseMemoryBlock] = Field(default_factory=dict)
    memory_blocks_template: BasePromptTemplate = Field()

    tokenizer_fn: Callable[[str], List] = Field(
        default_factory=get_tokenizer,
        exclude=True,
    )

    @classmethod
    def class_name(cls) -> str:
        return "WaterfallMemory"

    @model_validator(mode="before")
    @classmethod
    def validate_memory(cls, values: dict) -> dict:
        # Validate token limit like ChatMemoryBuffer
        token_limit = values.get("token_limit", -1)
        if token_limit < 1:
            raise ValueError("Token limit must be set and greater than 0.")
        tokenizer_fn = values.get("tokenizer_fn", None)
        if tokenizer_fn is None:
            values["tokenizer_fn"] = get_tokenizer()
        
        memory_blocks_template = values.get("memory_blocks_template", None)
        if memory_blocks_template is None:
            memory_blocks_template = ""
            for memory_block in values.get("memory_blocks", []):
                memory_blocks_template += "{{" + memory_block.name + "}}\n"
                template = RichPromptTemplate(
                    memory_blocks_template,
                )
                values["memory_blocks_template"] = template
        else:
            template_vars = memory_blocks_template.template_vars
            for memory_block in values.get("memory_blocks", []):
                if memory_block.name not in template_vars:
                    raise ValueError(f"Memory block {memory_block.name} not found in template.")
        # Potentially validate memory_blocks if needed
        return values

    @classmethod
    def from_defaults(
        cls,
        chat_history: Optional[List[ChatMessage]] = None,
        chat_store: Optional[BaseChatStore] = None,
        chat_store_key: str = DEFAULT_CHAT_STORE_KEY,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
        memory_blocks: Optional[List[BaseMemoryBlock]] = None,
        tokenizer_fn: Optional[Callable[[str], List]] = None,
    ) -> "WaterfallMemory":
        """Initialize WaterfallMemory."""

        chat_store = chat_store or SimpleChatStore()
        if chat_history is not None:
            chat_store.set_messages(chat_store_key, chat_history)

        return cls(
            token_limit=token_limit,
            tokenizer_fn=tokenizer_fn or get_tokenizer(),
            chat_store=chat_store,
            chat_store_key=chat_store_key,
            memory_blocks=memory_blocks or [],
        )
    
    async def aget(self, input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]:
        block_contents = await asyncio.gather(*[
            memory_block.aget(input, **kwargs)
            for memory_block in self.memory_blocks
        ])

        block_messages = self.memory_blocks_template.format_messages(
            **{
                memory_block.name: block_content
                for memory_block, block_content in zip(self.memory_blocks, block_contents)
            }
        )

        buffer_messages = ...