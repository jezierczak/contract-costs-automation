"""
Company domain module.

Architectural rules:
1. CandidateProvider may read repository
2. ConfidenceEvaluator MUST NOT read repository
3. SelectionService MUST NOT mutate data
4. ApplyService is the ONLY place allowed to mutate Company
5. LLM usage is allowed ONLY in SelectionService
"""
