# Known Risks

## Week 8/9 Risk List

- Gmail/MCP OAuth setup complexity may require additional credentials and extra testing time.
- HuggingFace model download (~330MB) on first run requires a stable internet connection.
- ChromaDB is empty until populated, so RAG context may show "No historical context available yet" until reports are indexed.
- Signal classifier thresholds may need tuning on real JotForm data versus synthetic mock data.
- Streamlit drill-down UI (Option A) is not yet built, so users cannot currently drill down into details.
- Lack of peer review feedback or slow review cycles could delay Week 9 quality improvements.
- Failure to obtain non-team HITL validation evidence may weaken the checkpoint submission.
- Backlog completion below the 80% target could jeopardize Week 10 demo readiness.
- Technical report draft sections 1-3 incomplete or shallow may reduce the quality of the checkpoint deliverable.
- Invalid HITL inputs are silently ignored — pipeline completes without action
