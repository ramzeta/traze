from fastapi import FastAPI
from consumers.trace_consumer import start_consumer
from queries.trace_queries import router as trace_router

app = FastAPI()
app.include_router(trace_router)

start_consumer()