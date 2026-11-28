# hidden "thinking" section (chain of thought), and Groq streams those tokens as chunks too
import os

from dotenv import load_dotenv

load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
from langchain.chat_models import (
    init_chat_model,  # Code you may want to make provider-agnostic
)

model = init_chat_model("groq:openai/gpt-oss-20b")
## Singel Request
# response = model.invoke("Explain how a bicycle stays upright when moving.")
# print(response.content)

## Stream
for chunk in model.stream("Write me a 300 words paragraph on how a bicycle stays balanced while moving"):
    print(chunk.text, end="|", flush=True)