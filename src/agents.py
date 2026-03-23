import base64
import io
import os
import tempfile
from pathlib import Path
from openai import OpenAI
from pypdf import PdfReader

from anthropic import AnthropicVertex
from anthropic.types import (
    Base64PDFSourceParam,
    DocumentBlockParam,
    MessageParam,
    TextBlockParam,
)
from dotenv import load_dotenv
from IPython.display import Markdown, display

from helpers import authenticate


class PZUAgent:
    def __init__(self) -> None:
        load_dotenv()
        # credentials, project_id = authenticate()
        # self.client = AnthropicVertex(
        #     project_id=project_id,
        #     region="global",
        #     access_token=credentials.token,
        # )
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        with Path("../data/Zakres_swiadczen_zdrowotnych_Optimum.pdf").open("rb") as file:
            self.pdf_data = base64.standard_b64encode(file.read()).decode("utf-8")

        pdf_bytes = base64.b64decode(self.pdf_data)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        self.text = "\n".join(p.extract_text() or "" for p in reader.pages)

    def answer_query(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert medical care agent designed to assist with coverage queries. "
                        "Use the provided documents to answer questions about medical care policies. "
                        "If the information is not available in the documents, respond with 'I don't know'"
                    )
                 },
                {
                    "role": "user",
                    "content": f"{self.text}\n\nQuestion: {prompt}"
                },
            ],
        )
        print(response)
        return response.choices[0].message.content

# if __name__ == '__main__':
#
#     print("Running Health Insurance Policy Agent")
#     agent = PZUAgent()
#     prompt = "How much would I pay for mental health therapy?"
#
#     response = agent.answer_query(prompt)
#     display(Markdown(response))