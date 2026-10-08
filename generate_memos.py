import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TOKEN")

prompt = """
Generate a JSON list containig exactly 20 distinct corporate memos for an IT conulting company.
Respond ONLY with a valid JSON array, with no markdown code fences and no extra text.

Role distribution:
- 8 memos for ["Employee", "Manager", "Executive"] (general policies, equipment, office rules)
- 7 memos for ["Manager", "Executive"] (team budgets, performance evaluations, promotions)
- 5 memos for ["Executive"] (confidential acquistions, executive pay, strategic audits)

Each object in the array must follow this exact schema:
{
  "id":1,
  "title": "String",
  "departement" : "HR" | "Finance" | "Engineering" | "Operations",
  "allowed_roles" : ["Employee", "Manager", "Executive"],
  "content" "2 to 3 sentences with specific figures and policies",
  "test_query": "A question answerable only with this content",
  "expected_answer" : "Short factual answer"
}

"""

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
    data=json.dumps(
        {
            "model": "inclusionai/ling-3.0-flash:floor",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "memos.json",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "memos": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "title": {"type": "string"},
                                        "departement": {
                                            "type": "string",
                                            "enum": ["HR", "Finance", "Engineering", "Operations"],
                                        },
                                        "allowed_roles": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                        },
                                        "content": {"type": "string"},
                                        "test_query": {"type": "string"},
                                        "expected_answer": {"type": "string"},
                                    },
                                    "required": [
                                        "id",
                                        "title",
                                        "departement",
                                        "allowed_roles",
                                        "content",
                                        "test_query",
                                        "expected_answer",
                                    ],
                                    "additionalProperties": False,
                                }
                            }
                        },
                        "required": ["memos"],
                        "additionalProperties": False,
                    },
                },
            },
        }
    ),
)

res_json = response.json()
content = res_json["choices"][0]["message"]["content"].strip()
# print(content)
# print(res_json["choices"][0]["message"]["content"])

if content.startswith("```"):
    content = content.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
    
data = json.loads(content)
memos = data.get("memos", data)

with open("memos.json", "w", encoding="utf-8") as f:
    json.dump(memos, f, indent=2, ensure_ascii=False)

