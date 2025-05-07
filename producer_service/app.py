from fastapi import FastAPI, Request
from commands.trace_publisher import publish_trace_event

app = FastAPI()

@app.middleware("http")
async def trace_middleware(request: Request, call_next):
    body = await request.body()
    response = await call_next(request)
    publish_trace_event(
        path=str(request.url.path),
        method=request.method,
        status=response.status_code,
        body=body.decode('utf-8')
    )
    return response

@app.post("/acciones")
async def ejecutar_accion(data: dict):
    return {"status": "OK", "message": "Acción ejecutada"}