# Problems LangChain Solves

LangChain provides a common framework for building applications powered
by language models. It reduces the amount of provider-specific
integration code and gives you reusable components for prompts,
workflows, retrieval, tools, and observability.

## At a glance

  ----------------------------------------------------------------------------------
  Problem area            Without LangChain       With LangChain
  ----------------------- ----------------------- ----------------------------------
  **Multiple model        Learn and maintain a    Use a common interface and switch
  providers**             separate SDK and        supported models with minimal code
                          integration for each    changes.
                          provider.               

  **Prompt management**   Build prompt strings    Create reusable prompt templates
                          manually and scatter    with named variables.
                          them throughout the     
                          codebase.               

  **Chaining steps**      Write glue code to      Compose steps using the Runnable
                          connect prompt          interface and the `\|` operator:
                          construction, model     `prompt \| model \| parser`.
                          calls, and output       
                          parsing.                

  **Structured output**   Parse raw text and      Use supported model integrations
                          validate the result     such as
                          yourself.               `with_structured_output(Schema)`
                                                  to request schema-shaped,
                                                  validated data.

  **Tools and function    Adapt tool definitions  Define tools using a common
  calling**               and calling logic to    abstraction and use them with
                          each provider's format. compatible models.

  **RAG (chat with your   Build document loading, Use integrations and reusable
  documents)**            splitting, embedding,   components for loaders, splitters,
                          vector storage, and     embeddings, vector stores, and
                          retrieval code          retrievers.
                          yourself.               

  **Memory and chat       Maintain message lists  Integrate chat history and
  history**               and conversation state  persistence; for more advanced
                          manually.               stateful workflows, use LangGraph.

  **Observability**       Add custom logging and  Trace application runs with
                          debugging around each   LangSmith and use its evaluation
                          step.                   capabilities.

  **Agents and            Write custom loops for  Build stateful, multi-step agent
  workflows**             tool calls, retries,    workflows with LangGraph.
                          branching, and state    
                          management.             
  ----------------------------------------------------------------------------------

## Example: composing a simple chain

``` python
chain = prompt | model | parser
result = chain.invoke({"topic": "LangChain"})
```

Each component has a defined role:

1.  **Prompt** -- formats the input using a reusable template.
2.  **Model** -- sends the formatted messages to the language model.
3.  **Parser** -- converts the model response into the required output
    format.

## Important distinction

LangChain does not remove the need to understand the underlying model
provider, APIs, or application design. It provides common abstractions
and integrations that reduce repetitive integration work.

Some capabilities also depend on the selected model and integration. For
example, structured output and tool calling require support from the
model or provider integration. LangGraph is the recommended layer for
more complex, stateful agent workflows, while LangSmith provides tracing
and evaluation.

## Summary

**LangChain helps standardize the building blocks of LLM applications.**
It is especially useful when an application needs reusable prompts,
model-provider flexibility, retrieval, tool integration, or composable
processing steps.

## | TypedDict | dataclass | Pydantic BaseModel |
**Plain Python dataclasses do not validate at runtime.** Like TypedDict, the type hints are just hints. The difference is that a dataclass gives you an object with attribute access instead of a dict.

**Proof**

```python
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError

@dataclass
class ContactDC:
    name: str
    email: str
    phone: str

class ContactPD(BaseModel):
    name: str
    email: str
    phone: str

print(ContactDC(name=123, email=None, phone=["x"]))   # works, no error

try:
    ContactPD(name=123, email=None, phone=["x"])
except ValidationError as e:
    print(e)                                           # raises
```

**Main differences**

| | TypedDict | dataclass | Pydantic BaseModel |
|---|---|---|---|
| Result at runtime | `dict` | class instance | class instance |
| Access | `r["name"]` | `r.name` | `r.name` |
| Runtime validation | No | No | Yes |
| Type coercion (`"25"` → `25`) | No | No | Yes (in default mode) |
| Field descriptions for the LLM | via `Annotated` | not built in | `Field(description=...)` |
| Extras (`.model_dump()`, JSON schema, constraints like `ge=0`) | No | No | Yes |


**When to use which**

- **Pydantic**: the default choice for extraction, agents, and anything where wrong or missing fields would cause problems. Use it when you want validation, constraints, nested models, or rich descriptions.
- **dataclass**: when you want a lightweight object with attribute access and trust the output, or your codebase already uses dataclasses. You can add validation with `from pydantic.dataclasses import dataclass`.
- **TypedDict**: when you want a plain dict, for example to pass straight into JSON or other dict-based code, and you don't need validation.