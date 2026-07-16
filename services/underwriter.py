from openai import OpenAI

import os

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)

def calculate_underwriting(invoice):

    prompt=f"""

You are an institutional credit committee.

Invoice:

{invoice}

Return ONLY JSON.

{{

"grade":"",

"risk_score":0,

"apr":0,

"fraud_probability":0

}}

"""

    response=client.chat.completions.create(

        model="meta-llama/llama-3.3-70b-instruct:free",

        messages=[

            {

                "role":"user",

                "content":prompt

            }

        ]

    )

    import json

    return json.loads(

        response.choices[0].message.content

    )