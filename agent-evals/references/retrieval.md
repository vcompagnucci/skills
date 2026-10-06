# Retrieval and abstention

## Retrieval

Evaluate retrieval apart from the answer. A wrong answer from the right article and a right-sounding answer from the wrong one need different fixes.

- **Ground truth by hand first,** for real questions. To scale, for each chunk extract one self-contained fact and write a question only that fact answers, returned as {fact, question}. Add distractor questions using wording from similar chunks that lack the answer. Keep only questions a few-shot rater scores 4 or 5 of 5 for realism.
- **Once live, rebuild ground truth daily from yesterday's real searches.** Sample the points where the agent searched, label the articles that would best have resolved the issue at that point (the answer plus the background it needs), and compute recall, precision, and NDCG per knowledge base. A fixed set goes stale as articles and policies change. If a model labels the golden set, validate it against human labels first. At Sierra, recall gains tracked resolution gains of up to 16 points.
- **Measure what retrieval costs with a gold-documents run.** Run each knowledge-heavy case twice, once with the agent's own retrieval and once with the needed documents handed to it. The gap is the retrieval loss, and the gold-documents score is the ceiling that prompt or reasoning work can reach without fixing search. On τ-knowledge the best agent passed 25.5% of tasks with its own retrieval and about 40% with the documents given.
- **Metric by question.** One fact: MRR. Several articles needed: recall@k. Ranking after a reranker: precision@k or NDCG@k. k is 1 to 2 for lookups, 5 to 10 for synthesis.
- **Filter before ranking.** Apply product and country filters before similarity. The right article for one market ranked below a similar one for another is a retrieval failure the answer can't fix.
- **Grade faithfulness claim by claim.** Split the reply into atomic claims, label each against the instructions, tool definitions, tool results, and retrieved articles, and fail the reply if any claim is unsupported or contradicted, even a true one: for a customer-facing agent an unsourced fact is a policy risk. Check structured facts (amounts, dates, ids) in code. The LLM groundedness verdict flipped on 10% to 21% of identical reruns, so it feeds a trend and a human-review queue, never a gate on a single run.
- **Read the failure off the metrics.** Low context relevance: fix retrieval (filters, chunking, query). Good context with an unfaithful answer: fix generation. Faithful but not answering: the model used the wrong section.
- **Chunk size and overlap are parameters.** Grid-search them against recall@k, and prepend the title and section heading to each chunk.
- **Search again when the conversation changes topic,** and test that the agent does.
- Never grade answers with ROUGE, BERTScore, or cosine similarity. They reward wording, not correctness.

## Abstention

Keep a balanced set of answerable and unanswerable questions, including cases where the data is missing or inconsistent and the right answer is "I can't tell from here". An agent never tested on the unanswerable half learns to guess.

- **Score three outcomes, never accuracy alone:** correct, wrong, and abstained or escalated. Accuracy ranks a guessing agent above a careful one. On SimpleQA a model with 24% correct, 75% wrong, and 1% abstained beat on accuracy one with 22% correct, 26% wrong, and 52% abstained.
- **For one number, use the abstention score against a confidence target t** (statistics.md), with t stated in the agent's instructions and chosen from the cost of a wrong answer. Answering then beats abstaining only when the agent's confidence is above t.
