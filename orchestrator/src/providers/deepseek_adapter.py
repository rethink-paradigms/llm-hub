from .stub_adapter import StubAdapter

class DeepSeekAdapter(StubAdapter):
    def __init__(self):
        super().__init__("deepseek")
