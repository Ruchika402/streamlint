import json
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add the backend directory to the path so we can import our services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from reviews.services.static import run_ruff
from reviews.services.prompt import build_prompt
from reviews.services.parser import parse_stream_chunk
from google import genai
from google.genai import types

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

async def evaluate():
    with open(os.path.join(os.path.dirname(__file__), 'cases.json')) as f:
        cases = json.load(f)

    results = {
        "ruff": {"true_positives": 0, "false_positives": 0, "total_real": 0},
        "ai": {"true_positives": 0, "false_positives": 0, "total_real": 0},
        "hybrid": {"true_positives": 0, "false_positives": 0, "total_real": 0}
    }

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    for case in cases:
        print(f"Evaluating {case['id']}...")
        real_issues = case["real_issues"]
        results["ruff"]["total_real"] += len(real_issues)
        results["ai"]["total_real"] += len(real_issues)
        results["hybrid"]["total_real"] += len(real_issues)

        # 1. Ruff Only
        ruff_findings = run_ruff(case["code"], case["language"])
        ruff_lines = {f["line"] for f in ruff_findings}
        
        ruff_tp = sum(1 for issue in real_issues if issue["line"] in ruff_lines)
        results["ruff"]["true_positives"] += ruff_tp
        results["ruff"]["false_positives"] += len(ruff_lines) - ruff_tp

        # 2. AI Only
        prompt = build_prompt(case["code"], case["language"], [])
        ai_lines = set()
        
        try:
            response = await client.aio.models.generate_content_stream(
                model=model_name, contents=prompt, config=types.GenerateContentConfig(max_output_tokens=1000)
            )
            
            buffer = ""
            async for chunk in response:
                if chunk.text:
                    parsed, buffer = parse_stream_chunk(chunk.text, buffer)
                    for item in parsed:
                        if item["type"] == "issue":
                            ai_lines.add(item["data"]["line"])
        except Exception as e:
            print(f"  AI failed for {case['id']}: {e}")

        ai_tp = sum(1 for issue in real_issues if issue["line"] in ai_lines)
        results["ai"]["true_positives"] += ai_tp
        results["ai"]["false_positives"] += len(ai_lines) - ai_tp

        # 3. Hybrid
        hybrid_lines = ruff_lines.union(ai_lines)
        hybrid_tp = sum(1 for issue in real_issues if issue["line"] in hybrid_lines)
        results["hybrid"]["true_positives"] += hybrid_tp
        results["hybrid"]["false_positives"] += len(hybrid_lines) - hybrid_tp

    # Print the report
    print("\n--- EVALUATION RESULTS ---")
    print(f"{'Mode':<10} | {'Recall':<10} | {'Precision':<10} | {'False Positives'}")
    print("-" * 55)
    for mode, data in results.items():
        recall = data["true_positives"] / data["total_real"] if data["total_real"] else 0
        total_reported = data["true_positives"] + data["false_positives"]
        precision = data["true_positives"] / total_reported if total_reported else 0
        print(f"{mode:<10} | {recall:.2f}       | {precision:.2f}        | {data['false_positives']}")

if __name__ == "__main__":
    asyncio.run(evaluate())