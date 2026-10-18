
from tavily import TavilyClient, TavilyKeylessLimitError

client = TavilyClient()

def web_search(query):
    try:
        response = client.search(query)
        return response
    except TavilyKeylessLimitError as e:
        return {"error": str(e)}

## Pass by value is like giving someone a photocopy: they can change their copy, but your original stays unchanged

# from tavily import TavilyClient

# def web_search(query,api_key_recevied):
#     # Step 1. Instantiating your TavilyClient
#     # tavily_client = TavilyClient(api_key="YOURAPI-KEY-HERE")
#     tavily_client = TavilyClient(api_key=api_key_recevied)

#     # Step 2. Executing a simple search query
#     response = tavily_client.search(query)

#     # Step 3. That's it! You've done a Tavily Search!
#     return response