from .stub_adapter import StubAdapter

class QwenAdapter(StubAdapter):
    def __init__(self):
        super().__init__("qwen")
