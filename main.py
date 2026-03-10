from app.workflows.fetch_workflow import trigger_fetch

result = trigger_fetch(
    "AVGO",
    [2022, 2023, 2024]
)
print(result)
