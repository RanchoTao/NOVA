"""NOVA CLI: roll, challenge, handoff, catalog and localhost UI."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .catalog import OPERATORS, load_seeds
from .engine import NovaEngine, artifact, dump_json
from .llm import ChatJSONClient, ModelError
from .review import challenge, handoff, read_card_file


def make_model(args: argparse.Namespace):
    if args.provider == "template":
        return None
    return ChatJSONClient(base_url=args.base_url, model=args.model, timeout=args.timeout)


def write_result(result: dict, destination: str | None, overwrite: bool = False):
    content = dump_json(result)
    if destination:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w" if overwrite else "x", encoding="utf-8") as stream:
            stream.write(content)
        print(f"Saved: {path}", file=sys.stderr)
    else:
        sys.stdout.write(content)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nova", description="NOVA / 震撼首发！假设破坏科研构想引擎")
    sub = parser.add_subparsers(dest="command", required=True)

    def provider_arguments(cmd):
        cmd.add_argument("--provider", choices=("template", "model"), default="template",
                         help="template=离线演示；model=真实大模型构想，需配置密钥")
        cmd.add_argument("--base-url", default=None, help="NOVA_BASE_URL 的命令行覆盖")
        cmd.add_argument("--model", default=None, help="NOVA_MODEL 的命令行覆盖")
        cmd.add_argument("--timeout", type=float, default=60.0)

    roll = sub.add_parser("roll", help="摇出构想并生成结构化卡片")
    provider_arguments(roll)
    roll.add_argument("--count", type=int, default=3)
    roll.add_argument("--seed", type=int, default=None, help="随机种子（模型生成文本不保证确定）")
    roll.add_argument("--domain", default=None)
    roll.add_argument("--operator", choices=tuple(OPERATORS), default=None)
    roll.add_argument("--out", default=None)
    roll.add_argument("--force", action="store_true", help="覆盖输出文件")

    review = sub.add_parser("challenge", help="输出初步反驳清单，不签发原创性/科学证明")
    provider_arguments(review)
    review.add_argument("file")
    review.add_argument("--idea-id")
    review.add_argument("--out")
    review.add_argument("--force", action="store_true")

    export = sub.add_parser("handoff", help="输出待复核 RanchoResearch 交接提案")
    export.add_argument("file")
    export.add_argument("--idea-id")
    export.add_argument("--out")
    export.add_argument("--force", action="store_true")

    sub.add_parser("catalog", help="输出当前假设种子与破坏算子")

    serve = sub.add_parser("serve", help="启动仅监听本地的老虎机界面")
    provider_arguments(serve)
    serve.add_argument("--port", type=int, default=8765)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "catalog":
            write_result({"operators": OPERATORS, "seeds": [
                {"id": s["id"], "domain": s["domain"], "assumption": s["assumption"]}
                for s in load_seeds()]}, None)
        elif args.command == "roll":
            result = artifact(NovaEngine(model=make_model(args)).roll(
                count=args.count, seed=args.seed, domain=args.domain, operator=args.operator))
            write_result(result, args.out, args.force)
        elif args.command == "challenge":
            card = read_card_file(args.file, args.idea_id)
            result = challenge(card, model=make_model(args)).to_dict()
            write_result(result, args.out, args.force)
        elif args.command == "handoff":
            card = read_card_file(args.file, args.idea_id)
            write_result(handoff(card), args.out, args.force)
        elif args.command == "serve":
            from .webapp import serve_local
            serve_local(NovaEngine(model=make_model(args)), args.port)
        else:
            parser.error("unknown command")
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError,
            json.JSONDecodeError, ModelError) as exc:
        print(f"NOVA error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
