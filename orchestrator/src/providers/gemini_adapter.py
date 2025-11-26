from .stub_adapter import StubAdapter

class GeminiAdapter(StubAdapter):
    def __init__(self):
        super().__init__("gemini")
