from fastapi import FastAPI
from fastapi import Request
import uvicorn

app=FastAPI(title="my first app",
            description=(" this app is for learning fastapi"
                         "Handle creation, tracking of delivery systems"),
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json"
)

@app.get("/")
def read_root():
    """this is our doc string , this is the root endpoint"""
    # FastAPI convert this dict into JSON
    return {"message":"Weclome to this worderfull app", "status":"healthy"}

@app.get("/about")
def about():
    return{
        "service":"order-service",
        "team": "backend platform",
        "version": "1.0.0",
        "verified":True
    }

@app.get("/debug/info")
def webrequest_info(request: Request):
    """Inspecting the raw request"""
    return{
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        # "headers2": request.headers,
        "path_params": request.path_params,
        "query_params": dict(request.query_params)
    }
    