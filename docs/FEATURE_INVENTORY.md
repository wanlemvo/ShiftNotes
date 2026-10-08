# Feature Inventory

This inventory describes the active `demo/` implementation. Historical notebooks
and archived RAG code are not evidence of features in the current app.

| Capability | Implementation | Evidence / limitation |
| --- | --- | --- |
| JotForm ingestion | [client](../demo/src/shiftnotes/jotform_client.py), [normalizer](../demo/src/shiftnotes/normalize.py) | [tests](../tests/test_jotform_normalize.py); one-page fetch, fixed aliases |
| Completeness and deduplication | [baseline](../demo/src/shiftnotes/baseline.py) | [dataset tests](../tests/test_final_mock_dataset.py); requires expected schedule |
| Semantic extraction | [semantic](../demo/src/shiftnotes/semantic.py) | [tests](../tests/test_semantic_extraction.py); evidence, retry, cache, fallback |
| Weekly/monthly briefings | [briefings](../demo/src/shiftnotes/briefings.py) | [tests](../tests/test_final_briefings.py); synthetic defaults |
| Priority tiers and previews | [email preview](../demo/src/shiftnotes/email_preview.py) | [product tests](../tests/test_product_workflow.py); rule-based, not financial ranking |
| Gmail delivery | [Gmail](../demo/src/shiftnotes/gmail_delivery.py) | [tests](../tests/test_gmail_delivery.py), [historical log](../demo/evidence/final/gmail_delivery.log); explicit send |
| Dashboard, trends, filters | [projection](../demo/src/shiftnotes/dashboard.py), [UI](../demo/src/shiftnotes/dashboard_view.py) | [tests](../tests/test_dashboard.py); bundled dataset |
| Sources and corrections | [product](../demo/src/shiftnotes/product.py), [correction graph](../demo/src/shiftnotes/correction_graph.py) | [tests](../tests/test_product_workflow.py); deterministic interpretation, JSON/SQLite |
| Stateful retry/fallback demo | [graph](../demo/src/shiftnotes/graph.py) | [tests](../tests/test_langgraph_workflow.py); separate teaching flow with pre-finalization approval |

See [verification](VERIFICATION.md) for executed checks. Synthetic tests demonstrate
behavior, not production reliability or measured business benefit. No universal
form connector, mailbox parser, or scheduled live service is implemented.
