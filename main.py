import logging
# from app.workflows.analysis_workflow import start_analysis

logging.basicConfig(level=logging.WARNING)

# result = start_analysis(
#     "AAPL"
# )
# print(result)

# from app.utils.fetch import fetch_filing
# from app.utils.preprocessing import prepare_chunks_with_metadata
# 
# filing1 = fetch_filing("AAPL", 2024)
# filing2 = fetch_filing("AAPL", 2025)
# result = prepare_chunks_with_metadata([filing1.value, filing2.value])
# print(result)

from app.workflows.analysis_workflow import dr_analysis
import json

result = dr_analysis("AAPL", 2023)
print(result)
# print(result)
