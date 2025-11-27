import os
import sys

# Make orchestrator package importable when running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from orchestrator.src.runtime.llm_client import get_llm_client
from orchestrator.src.runtime.types import Message


def main() -> int:
    config_path = os.path.join(os.path.dirname(__file__), "llm_orchestrator.yaml")

    try:
        client = get_llm_client(config_path)
        messages = [
            Message(role="system", content="You are a helpful assistant."),
            Message(role="user", content="Hello, world!"),
        ]

        print("Running llm.preprocess...")
        response = client.run(role="llm.preprocess", messages=messages)
        print("LLMResponse:", response)
        return 0
    except Exception as exc:
        print(f"Orchestrator error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
