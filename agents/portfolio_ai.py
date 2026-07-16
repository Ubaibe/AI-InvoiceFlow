import os

from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)


def generate_portfolio_commentary(
    invoice,
    allocation
):

    prompt = f"""
You are the Head of Portfolio Construction of a global institutional private credit fund.

The Investment Committee has approved financing.

Prepare a portfolio allocation commentary.

Invoice

Buyer:
{invoice.buyer}

Industry:
{invoice.industry}

Amount:
${invoice.amount}

Risk Score:
{invoice.risk_score}

APR:
{invoice.apr}

Portfolio

Portfolio:
{allocation["portfolio"]}

Investment:
{allocation["investment"]}

Weight:
{allocation["weight"]}

Sector Weight:
{allocation["sector_weight"]}

Expected Return:
{allocation["expected_return"]}

Remaining Capacity:
{allocation["capacity"]}

Risk Bucket:
{allocation["risk_bucket"]}

Write ONLY Markdown.

Maximum 150 words.

Use these headings:

## Portfolio Rationale

## Diversification Impact

## Final Allocation Decision
"""

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[

            {

                "role":"user",

                "content":prompt

            }

        ],

        temperature=.3

    )

    return response.choices[0].message.content