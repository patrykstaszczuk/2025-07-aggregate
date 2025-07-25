from fastapi import FastAPI

from app.api.transactions import endpoints as transaction_endpoints

app = FastAPI(title="Transaction Aggregator")
app.include_router(transaction_endpoints.router)
