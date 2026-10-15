"""Optional paid step: send the prepared messages to OpenAI, save the draft, check its numbers.

Needs `pip install openai` and OPENAI_API_KEY. Makes one API call and asks first.
Nothing is sent anywhere else and nothing is published.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from check_agent_output import untraceable_numbers  # noqa: E402
from prepare_agent_input import prepare  # noqa: E402

DEFAULT_MODEL = "gpt-4.1-mini"


def call_openai(messages: list[dict], model: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("The openai package is not installed. Run: python -m pip install openai")
    response = OpenAI().chat.completions.create(model=model, messages=messages, temperature=0.2)
    return response.choices[0].message.content or ""


def main(argv=None, model_call=call_openai) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--summary", type=Path, required=True, help="summary.json from analyze.py")
    parser.add_argument("--output", type=Path, required=True, help="Where to save the draft (.md)")
    parser.add_argument("--yes", action="store_true", help="Skip the cost question")
    args = parser.parse_args(argv)

    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set. Nothing was sent.")
        print("To see an agent draft without a key, open agent_output.md in this folder.")
        return 1
    if args.output.exists():
        print(f"{args.output} already exists. Choose another path. Nothing was sent.")
        return 1

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    payload = prepare(summary)
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)

    if not args.yes:
        answer = input(f"This sends summary.json to OpenAI ({model}) in 1 paid call. Continue? [yes/no]: ")
        if answer.strip().lower() not in {"y", "yes"}:
            print("Stopped. Nothing was sent.")
            return 0

    draft = model_call(payload["messages"], model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    provenance = (f"> Agent output from {model} via run_agent.py. Data label: "
                  f"{summary.get('data_label', 'unverified')}. Not reviewed by a person.\n\n")
    args.output.write_text(provenance + draft.strip() + "\n", encoding="utf-8")
    print(f"Draft saved to {args.output}")

    problems = untraceable_numbers(draft, summary)
    if problems:
        print(f"Warning: {len(problems)} number(s) in the draft are not in summary.json:")
        for p in problems:
            print("  " + p)
        print("Fix or remove them before anyone reads the draft.")
        return 2
    print("All numbers in the draft trace to summary.json. A person still needs to review the wording.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
