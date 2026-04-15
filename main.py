import logging
from app.workflows.analysis_workflow import start_analysis

logging.basicConfig(level=logging.WARNING)

result = start_analysis(
    "AAPL"
)
print(result)
