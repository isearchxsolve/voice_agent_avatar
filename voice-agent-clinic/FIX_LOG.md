# Audit Fix Log

| Audit issue | Resolution | Regression evidence |
|---:|---|---|
| 1 | Dental prompt is valid Python with no Markdown fence. | `test_each_vertical_faq_is_an_array_of_question_answer_records`; `py_compile` gate |
| 2 | Dental onboarding is `onboarding.json`, not executable JSON-in-Python. | JSON/vertical data checks |
| 3 | Tests use `agent.middleware.guardrails`. | `tests/unit/test_agent.py` import/run |
| 4 | Webhook `routes` and `services` contain package markers. | webhook module import check |
| 5, 11 | Webhook requirements and Dockerfile exist and are pinned/non-root. | compose config gate |
| 6, 7 | Vertical/pricing FAQs are JSON arrays. | vertical FAQ matrix |
| 8 | HeyGen stream status uses React state. | widget build gate |
| 9 | Pure selector chooses only remote avatar video tracks. | Vitest `2/2` |
| 10 | `package-lock.json` is committed for `npm ci`. | `npm ci` gate |
| 12, 22 | Agent health/metrics sidecar and deploy probe added. | health route unit/import gate |
| 13 | Dict, JSON-string, plain-string metadata is normalized and allowlisted. | metadata matrix |
| 14, 16 | Agent cleanup awaits every client even when one fails. | cleanup implementation/contract suite |
| 15 | Date/time imports are top-level. | `agent.main` import gate |
| 17 | CRM uses timezone-aware `datetime.now(timezone.utc)`. | existing CRM contract test |
| 18 | Retriever loads once into an instance cache. | retriever implementation/matrix |
| 19 | SIP defaults and supplied URI gain `sip:` prefix. | Twilio handler contract |
| 20 | Removed unused background-task parameter. | route signature |
| 21 | Deployment uses `docker compose` v2. | deploy script/compose gate |
| 23 | High-risk PII naming/documentation is explicit; names remain allowed. | 120 no-false-positive cases |
| 24 | No unused `sys` import in `agent.main`. | lint/import review |
| 25 | Chunk overlap validates parameters and never skips the tail. | 350 chunk boundary cases |
| 26 | Retriever removes punctuation before token comparison. | 250 tokenization cases |
| 27 | Pricing now states net ROI formula. | outreach formula review |
| 28, 29 | Avatar widget has no dead Daily track imports or unused state setter. | widget build gate |
| 30 | Prompt values are held in Python strings and safely consumable as text/JSON. | prompt-loading matrix |
