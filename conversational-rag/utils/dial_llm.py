# langchain wrapper for dial - so we can use it in chains

from typing import Any, List, Optional

from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

from utils.dial_client import DIALClient


def _message_to_dial(m: BaseMessage) -> dict:
    # langchain msg -> dial format (role, content)
    role = "user"
    if isinstance(m, HumanMessage):
        role = "user"
    elif isinstance(m, AIMessage):
        role = "assistant"
    elif isinstance(m, SystemMessage):
        role = "system"
    else:
        role = getattr(m, "type", "user")
        if role == "human":
            role = "user"
        elif role == "ai":
            role = "assistant"
    content = m.content if isinstance(m.content, str) else str(m.content)
    return {"role": role, "content": content}


class DIALChatModel(SimpleChatModel):
    # uses dial api for completions

    model: str = "gpt-4"

    def __init__(
        self,
        client: Optional[DIALClient] = None,
        model: str = "gpt-4",
        **kwargs: Any,
    ):
        super().__init__(model=model, **kwargs)
        self._dial_client = client or DIALClient(model=model)

    @property
    def _llm_type(self) -> str:
        return "dial"

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if not self._dial_client.client:
            return "DIAL client not initialized. Please set DIAL_API_KEY."
        dial_messages = [_message_to_dial(m) for m in messages]
        return self._dial_client.get_completion(
            dial_messages, model=kwargs.get("model") or self.model
        )
