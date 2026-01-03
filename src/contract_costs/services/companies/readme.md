## Company identification flow

This module follows a strict identification pipeline:

1. CandidateProvider → may read repository
2. ConfidenceEvaluator → MUST NOT read repository
3. SelectionService → MUST NOT write data
4. ApplyService → ONLY place allowed to mutate Company
5. LLM → allowed ONLY in SelectionService

Breaking these rules is considered an architectural violation.
