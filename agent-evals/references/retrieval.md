# Retrieval and abstention

## Retrieval

Evaluate retrieval apart from the answer: a wrong answer from the right article and a right-sounding answer from the wrong one need different fixes.

- **Ground truth by hand first,** for real questions. To scale: for each chunk, extract one self-contained fact and write a question only that fact answers, returned as {fact, question}. Add distractor questions using wording from similar chunks that lack the answer. Keep only questions a few-shot rater scores 4 or 5 of 5 for realism.
- **Metric by question.** One fact: MRR. Several articles needed: recall@k. Ranking after a reranker: precision@k or NDCG@k. k is 1 to 2 for lookups, 5 to 10 for synthesis.
- **Filter before ranking.** Apply product and country filters before similarity: the right article for one market ranked below a similar one for another is a retrieval failure the answer can't fix.
- **A correct fact that no retrieved article states is a faithfulness failure.** For a customer-facing agent an unsourced fact is a policy risk even when it's true.
- **Read the failure off the metrics.** Low context relevance: fix retrieval (filters, chunking, query). Good context with an unfaithful answer: fix generation. Faithful but not answering: the model used the wrong section.
- **Chunk size and overlap are parameters.** Grid-search them against recall@k, and prepend the title and section heading to each chunk.
- **Search again when the conversation changes topic,** and test that the agent does.
- Never grade answers with ROUGE, BERTScore, or cosine similarity: they reward wording, not correctness.

## Abstention

Keep a balanced set of answerable and unanswerable questions, including cases where the data is missing or inconsistent and the right answer is "I can't tell from here". An agent never tested on the unanswerable half learns to guess.
