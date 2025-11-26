from typing import Optional
from src.sp5_resolution_maps.types import ResolutionMaps, LLMResolution, StoreResolution, ResolutionStatus
from .types import ResolveOptions

class RuntimeResolver:
    def __init__(self, resolution_maps: ResolutionMaps):
        self.maps = resolution_maps

    def resolve_llm(self, project: str, env: str, role: str, options: Optional[ResolveOptions] = None) -> LLMResolution:
        """
        Resolves an LLM configuration for the given context.
        """
        key = (project, env, role)
        resolution = self.maps.llm.get(key)

        if resolution and resolution.status == ResolutionStatus.OK:
            return resolution

        # Handle fallbacks
        if options and options.fallbacks:
            for fallback_role in options.fallbacks:
                fallback_key = (project, env, fallback_role)
                fallback_res = self.maps.llm.get(fallback_key)
                if fallback_res and fallback_res.status == ResolutionStatus.OK:
                    return fallback_res

        # If we're here, we failed to resolve
        msg = "Role not found"
        if resolution:
            msg = resolution.message or "Unknown error"
            
        return LLMResolution(
            status=ResolutionStatus.ERROR,
            message=msg
        )

    def resolve_store(self, project: str, env: str, role: str) -> StoreResolution:
        """
        Resolves a storage configuration for the given context.
        """
        key = (project, env, role)
        resolution = self.maps.store.get(key)

        if resolution:
            return resolution
            
        return StoreResolution(
            status=ResolutionStatus.ERROR,
            message="Role not found"
        )
