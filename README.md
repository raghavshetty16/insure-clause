# ClauseCheck

Agentic RAG for health insurance claim adjudication.
Generative AI, Assignment 3 (group mini-project), Jio Institute.

Given a claim scenario and a policy wording, ClauseCheck finds the relevant clauses (waiting period, exclusions, room rent cap, sub-limit, co-payment, sum insured), reads the numbers out of them, and decides the claim. The verdict and the rupee amount come from a plain Python rules engine, not from the model. The model only finds clauses, extracts numbers and explains the decision, so every figure can be traced to a clause and page.

## How it works

```
policy PDFs -> clause-aware chunking -> Chroma (dense) + BM25 (keyword)
            -> reciprocal rank fusion -> cross-encoder rerank

parse_and_plan -> retrieve -> grade -+-> calculate -> adjudicate
                     ^               |
                     +---- retry ----+
```

- If a retrieved clause does not answer a check, the query is rewritten once and retried.
- If a check still fails, the claim is referred to a human instead of guessed.
- Retrieval is filtered to the selected policy, so one insurer's rules never leak into another's.

## Stack

| Part | Tool |
|---|---|
| Chat model | Groq, `openai/gpt-oss-120b` (override with `MODEL_NAME` in `.env`) |
| Embeddings | Ollama, `nomic-embed-text` (runs locally) |
| Vector store | Chroma (saved in `chroma_langchain_db/`) |
| Keyword search | BM25 |
| Re-ranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Agent graph | LangGraph |
| UI | Gradio |

## Folder layout

Keep these together. The notebook reads `data/` relative to its own location.

```
gen-ai-final-project/
  ClauseCheck.ipynb
  requirements.txt
  README.md
  .env                      # GROQ_API_KEY=...
  data/
    policies/
      manifest.json         # maps each PDF to insurer and product
      *.pdf
    gold/
      claims.json           # 20 labelled test scenarios
  chroma_langchain_db/      # created on first run
  eval_results/             # created by the evaluation cell
```

## Setup (Windows, VSCode)

**1. Install Ollama** from https://ollama.com/download, keep it running, then pull the embedding model once:

```powershell
ollama pull nomic-embed-text
```

**2. Get a Groq API key** from https://console.groq.com and create a file named `.env` next to the notebook:

```
GROQ_API_KEY=your_key_here
```

If you skip this, the notebook asks for the key when it runs.

**3. Create a virtual environment and install packages** (Python 3.12 recommended):

```powershell
uv venv .venv --python 3.12
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

Without `uv`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activate script, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**4. Open the folder in VSCode** (File > Open Folder), and install the **Python** and **Jupyter** extensions.

**5. Select the kernel.** Open `ClauseCheck.ipynb`, click Select Kernel (top right), then Python Environments, and choose your `.venv`. If it is not listed, choose Enter interpreter path and paste the full path to `.venv\Scripts\python.exe`.

## Running

1. Run the first code cell (the environment check). It prints `READY`, or lists what to fix.
2. Run the remaining cells in order, or use Run All.
3. The Gradio app launches from section 8 and opens at http://127.0.0.1:7860. Pick a policy, paste a claim or load an example, and press Adjudicate.

The first run is slow because it downloads the re-ranker models and embeds every chunk. Later runs reuse the saved index.

## Settings you may want to change

All in one cell near the top of the notebook (section 1) and in the evaluation cell (section 9):

| Setting | Meaning |
|---|---|
| `DENSE_K`, `BM25_K` | candidates fetched from each retriever |
| `RERANK_TOP_N` | clauses kept after re-ranking |
| `MAX_RETRIES_PER_CHECK` | query rewrites before a check is given up |
| `EVAL_CASES` | number of gold cases to evaluate (`None` = all 20) |
| `JUDGE` | turns the faithfulness judge on (one extra model call per case) |

## Evaluation

Section 9 compares ClauseCheck against a naive RAG baseline (fixed-size chunks, dense retrieval only, one model call for the verdict). Metrics: verdict accuracy, amount accuracy, citation accuracy, context recall, faithfulness and abstention rate. Results are saved to `eval_results/ablation.json`.

Groq's free tier allows about 200,000 tokens per day per model. The full 20-case run costs roughly 264,000, so the notebook defaults to 8 cases with the judge off. If the quota runs out mid-run, it stops cleanly and labels the table provisional.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Activate.ps1 : The module '.venv' could not be loaded` | Use `.\.venv\Scripts\Activate.ps1` (with the leading `.\`) |
| `File not found: requirements.txt` | `cd` into the folder that contains it, or pass the full path |
| `No module named 'langchain.prompts'` | Old LangChain import. This notebook already uses the new imports; reinstall from `requirements.txt` |
| `No module named pip` when using `%pip` | Do not install from inside the notebook. Install from the terminal with `uv pip install` |
| `Access is denied` during install | Close notebooks using that venv, or restart VSCode, then install again |
| Kernel cannot find installed packages | The kernel is not the `.venv`. Reselect it with Select Kernel |
| Check cell says Ollama is not running | Start the Ollama app, or run `ollama serve` |
| Check cell says `nomic-embed-text` is missing | Run `ollama pull nomic-embed-text` |
| Groq 404 or model not found | Set `MODEL_NAME` in `.env` to a chat model your account can use |
| Groq 429 / rate limit | Daily token limit reached. Wait, lower `EVAL_CASES`, or use a different model |
| Gradio app blank inside VSCode | Open http://127.0.0.1:7860 in your browser |
| Results look stale after editing chunking or PDFs | Delete `chroma_langchain_db/` and re-run the indexing cells |

## Limitations

- The policy documents are generated samples, not real insurer wordings. Real PDFs (tables, two-column layouts, scans) will need work in the clause splitter.
- Twenty gold scenarios show a direction, not a confidence interval.
- The rules engine applies room rent proportionate deduction to the whole bill, which is the common reading. Real policies differ.
- Faithfulness is scored by the same model that wrote the explanation, so read that number with care.
