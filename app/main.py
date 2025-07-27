from fastapi import FastAPI

from app.api.reports import endpoints as reports_endpoints
from app.api.transactions import endpoints as transaction_endpoints

app = FastAPI(title="Transaction Aggregator")
app.include_router(transaction_endpoints.router)
app.include_router(reports_endpoints.router)
