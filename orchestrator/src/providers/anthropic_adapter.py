from .stub_adapter import StubAdapter

class AnthropicAdapter(StubAdapter):
    def __init__(self):
        super().__init__("anthropic")
