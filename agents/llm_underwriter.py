import os
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(

    base_url="https://openrouter.ai/api/v1",

    api_key=os.getenv("OPENROUTER_API_KEY")

)


def generate_ai_credit_memo(invoice):
    prompt = f"""
    You are the Senior Credit Officer of a global institutional private credit fund.

    You are preparing a memorandum that will be presented directly to an investment committee considering financing this invoice.

    Write as an experienced institutional credit analyst.

    The report should read like an internal investment memo prepared by BlackRock, Apollo, Ares, Goldman Sachs Asset Management, or JPMorgan Private Credit.

    IMPORTANT:

    Return ONLY Markdown.

    Do NOT return JSON.

    Do NOT wrap the output in triple backticks.

    Use professional headings.

    Use tables where appropriate.

    Use bullet points.

    Use bold text for important conclusions.

    The memorandum should follow EXACTLY this structure.

    # AI CREDIT MEMORANDUM

    Prepared by: AI Underwriting Division

    ---

    ## Executive Summary

    Provide a concise executive overview of the transaction.

    ---

    ## Invoice Overview

    | Item | Value |
    |------|------|
    | Invoice Number | {invoice.invoice_number} |
    | Buyer | {invoice.buyer} |
    | Industry | {invoice.industry} |
    | Invoice Amount | {invoice.amount} |
    | Due Date | {invoice.due_date} |

    ---

    ## Credit Assessment

    | Metric | Assessment |
    |------|------|
    | Internal Risk Score | {invoice.risk_score} |
    | Credit Grade | {invoice.grade} |
    | Suggested APR | {invoice.apr}% |
    | Fraud Probability | {invoice.fraud_probability}% |

    Explain what these metrics imply.

    ---

    ## Buyer Assessment

    Evaluate the buyer's ability and willingness to pay.

    ---

    ## Industry Outlook

    Discuss the current industry outlook and how it affects repayment risk.

    ---

    ## Cash Flow Analysis

    Discuss expected payment certainty and invoice liquidity.

    ---

    ## Key Strengths

    Provide 4-6 bullet points.

    ---

    ## Key Risks

    Provide 4-6 bullet points.

    ---

    ## Fraud Assessment

    Evaluate whether the invoice exhibits suspicious characteristics.

    ---

    ## Investment Recommendation

    Conclude with one of:

    **APPROVE**

    **APPROVE WITH CONDITIONS**

    **REJECT**

    Then explain why.

    Finally provide:

    **Recommended APR**

    **Overall Confidence (%)**

    End with one short investment committee conclusion.
    """

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[

            {

                "role": "user",

                "content": prompt

            }

        ],

        temperature=0.3

    )

    return json.loads(

        response.choices[0].message.content

    )