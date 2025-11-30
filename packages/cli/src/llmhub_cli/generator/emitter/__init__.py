"""
SP10 - Machine Config Emitter: Build and emit machine config.

Exports:
    - MachineConfig (model)
    - build_machine_config, write_machine_config (functions)
"""
from .models import MachineConfig
from .builder import build_machine_config, write_machine_config

__all__ = [
    "MachineConfig",
    "build_machine_config",
    "write_machine_config",
]
