# from app.workflows.fetch_workflow import trigger_fetch
# 
# result = trigger_fetch(
#     "AVGO",
#     [2022, 2023, 2024]
# )
# print(result)

import logging
from app.workflows.analysis_workflow import start_analysis

logging.basicConfig(level=logging.WARNING)

result = start_analysis(
    "AVGO"
)
print(result)
