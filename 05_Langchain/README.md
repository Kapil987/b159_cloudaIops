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
