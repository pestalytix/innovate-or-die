# Innovation quality evaluator

Evaluate the proposed final answer without rewriting it. Score every dimension from 1 to 5:

- `novelty`: Did the search meaningfully leave the default conceptual neighborhood?
- `mechanism`: Are important proposals supported by intelligible causal mechanisms?
- `value`: Would these ideas matter materially if correct?
- `testability`: Can important assumptions be validated or falsified?
- `search_breadth`: Were genuinely different conceptual spaces examined?
- `assumption_awareness`: Were inherited assumptions actively challenged?
- `intellectual_independence`: Did the answer avoid simply telling the user what they seemed to want?
- `reality_contact`: Are facts, hypotheses, assumptions, and speculation distinguished?

Return the eight scores plus:

- `critical_problems`
- `revision_directions`

Require revision when any score is below 4 or `critical_problems` is nonempty. Identify specific deficiencies and the correction required. Do not rewrite the answer.
