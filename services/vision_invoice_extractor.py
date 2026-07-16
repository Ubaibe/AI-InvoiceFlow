import os
import json
import base64

from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def extract_invoice_data(image_path):

    with open(image_path, "rb") as f:
        image = base64.b64encode(f.read()).decode()

    prompt = """
You are an expert financial invoice parser.

Return ONLY valid JSON.

{
 "invoice_number":"",
 "buyer":"",
 "amount":"",
 "industry":"",
 "due_date":""
}

If a field is missing use "".

Do not explain anything.
"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[
            {
                "role": "user",
                "content": [

                    {
                        "type": "text",
                        "text": prompt
                    },

                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image}"
                        }
                    }

                ]
            }
        ]

    )

    content = response.choices[0].message.content

    print("\n===== RAW MODEL OUTPUT =====")
    print(content)
    print("============================\n")

    # Remove markdown code fences if present
    content = content.replace("```json", "")
    content = content.replace("```", "").strip()

    try:
        return json.loads(content)
        print("\n========== RAW RESPONSE ==========\n")
        print(content)
        print("\n==============================\n")
    except Exception:
        print("Model did not return valid JSON.")
        return {
            "invoice_number": "",
            "buyer": "",
            "amount": "",

        }