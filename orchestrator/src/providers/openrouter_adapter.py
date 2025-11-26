from .stub_adapter import StubAdapter

class OpenRouterAdapter(StubAdapter):
    def __init__(self):
        super().__init__("openrouter")
