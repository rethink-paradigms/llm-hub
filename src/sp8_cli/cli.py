import argparse
import sys
import os
import json
from src.sp1_config_loader.loader import load_static_config
from src.sp2_auth_registry.registry import build_auth_registry
from src.sp3_model_catalog.catalog import build_model_catalog
from src.sp4_storage_catalog.catalog import build_storage_catalog
from src.sp5_resolution_maps.maps import build_resolution_maps
from src.sp6_runtime_resolver.resolver import RuntimeResolver
from src.sp7_config_exporter.exporter import export_config

def main():
    parser = argparse.ArgumentParser(description="Resource Orchestrator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common args
    parser.add_argument("--config-dir", default="./config", help="Path to config directory")

    # resolve-llm
    parser_llm = subparsers.add_parser("resolve-llm", help="Resolve LLM config")
    parser_llm.add_argument("--project", required=True)
    parser_llm.add_argument("--env", required=True)
    parser_llm.add_argument("--role", required=True)

    # resolve-store
    parser_store = subparsers.add_parser("resolve-store", help="Resolve Store config")
    parser_store.add_argument("--project", required=True)
    parser_store.add_argument("--env", required=True)
    parser_store.add_argument("--role", required=True)

    # export-config
    parser_export = subparsers.add_parser("export-config", help="Export configuration")
    parser_export.add_argument("--project", required=True)
    parser_export.add_argument("--env", required=True)
    parser_export.add_argument("--format", default="json", choices=["json", "yaml", "env"])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # bootstrap
    try:
        static_config = load_static_config(args.config_dir)
        auth_registry = build_auth_registry(static_config)
        model_catalog = build_model_catalog(static_config, auth_registry)
        storage_catalog = build_storage_catalog(static_config)
        resolution_maps = build_resolution_maps(static_config, model_catalog, storage_catalog)
        resolver = RuntimeResolver(resolution_maps)
    except Exception as e:
        print(f"Error initializing Resource Orchestrator: {e}")
        sys.exit(1)

    if args.command == "resolve-llm":
        res = resolver.resolve_llm(args.project, args.env, args.role)
        print(res.model_dump_json(indent=2))
        if res.status != "ok":
            sys.exit(1)

    elif args.command == "resolve-store":
        res = resolver.resolve_store(args.project, args.env, args.role)
        print(res.model_dump_json(indent=2))
        if res.status != "ok":
            sys.exit(1)

    elif args.command == "export-config":
        try:
            output = export_config(resolution_maps, args.project, args.env, args.format)
            print(output)
        except Exception as e:
            print(f"Export failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
