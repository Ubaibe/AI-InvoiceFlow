import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("OpenRouter Key:", os.getenv("OPENROUTER_API_KEY"))

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)


def generate_credit_memo(

    invoice_number,

    buyer,

    amount,

    industry,

    due_date

):

    prompt = f"""

You are an institutional credit analyst.

Write a professional investment memo.

Invoice Number:
{invoice_number}

Buyer:
{buyer}

Amount:
${amount}

Industry:
{industry}

Due Date:
{due_date}

Return

• Buyer Assessment

• Invoice Quality

• Collection Risk

• Suggested Grade

• Suggested APR

• Investment Recommendation

"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[

            {

                "role":"user",

                "content":prompt

            }

        ]

    )

    return response.choices[0].message.content