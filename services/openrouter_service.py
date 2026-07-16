import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def stream_credit_memo(prompt):

    stream = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )

    for chunk in stream:

        if (
            chunk.choices
            and chunk.choices[0].delta.content
        ):

            yield chunk.choices[0].delta.content