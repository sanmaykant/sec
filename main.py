# import logging
# from app.workflows.analysis_workflow import start_analysis

# logging.basicConfig(level=logging.WARNING)

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








# import logging
# from app.workflows.disappearing_risks import dr_analysis
# 
# logging.basicConfig(level=logging.WARNING)
# 
# result = dr_analysis("AAPL", 2025)
# # print(result)
# # print(result)









from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.workflows.disappearing_risks import dr_analysis, dr_analysiss

app = FastAPI(title="SEC Analysis API")

class AnalysisRequest(BaseModel):
    ticker: str
    year: int

@app.post("/analyze")
async def trigger_analysis(request: AnalysisRequest):
    try:
        # Note: dr_analysis calls .get(), so this blocks the worker 
        # but allows the FastAPI event loop to remain responsive.
        result = dr_analysis(request.ticker, request.year)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyzee")
async def trigger_analysis(request: AnalysisRequest):
    try:
        # Note: dr_analysis calls .get(), so this blocks the worker 
        # but allows the FastAPI event loop to remain responsive.
        result = dr_analysiss(request.ticker, request.year)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "online"}
