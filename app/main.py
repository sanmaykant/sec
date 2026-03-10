from app.workflows.fetch_workflow import trigger_fetch

result = trigger_fetch(
    request.ticker,
    request.cik,
    request.years
)
print(result)
