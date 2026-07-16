import pdfplumber
import pytesseract
import tempfile

from PIL import Image
import json
from openai import OpenAI
import os

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)


def summarize_invoice(invoice_text):
    prompt = f"""
    You are an institutional credit analyst.

    Analyze this invoice.

    Return a short executive summary covering:

    - Buyer quality
    - Invoice quality
    - Possible fraud indicators
    - Collection risk

    Maximum 80 words.

    Invoice:

    {invoice_text}
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

def ocr_page(page):

    image = page.to_image(resolution=300)

    with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
    ) as tmp:

        image.save(tmp.name, format="PNG")

        text = pytesseract.image_to_string(

            Image.open(tmp.name)

        )

    return text

def extract_invoice_data(pdf_path):

    text = ""

    if pdf_path.lower().endswith(".pdf"):

        with pdfplumber.open(pdf_path) as pdf:

            text = ""

            for i, page in enumerate(pdf.pages):

                page_text = page.extract_text()

                print(f"PAGE {i + 1}")
                print("--------------------")
                print(page_text)
                print("--------------------")

                if page_text:
                    text += page_text + "\n"

    prompt = f"""
    You are an expert invoice parser.

    Below is the COMPLETE invoice text extracted from a PDF.

    Your task is to extract the fields below.

    Return ONLY valid JSON.

    Do NOT explain anything.

    If a field cannot be found, return an empty string.

    JSON format:

    {{
    "invoice_number":"",
    "buyer":"",
    "amount":"",
    "industry":"",
    "due_date":""
    }}

    Invoice Text:

    {text}
    """

    print("========== EXTRACTED PDF TEXT ==========")
    print(text)
    print("========================================")

    response = client.chat.completions.create(

        model="openrouter/free",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )

    content = response.choices[0].message.content

    try:

        data = json.loads(content)


    except Exception as e:

        print("========= RAW AI RESPONSE =========")

        print(content)

        print("===================================")

        raise e

    return data, text