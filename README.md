# Retrieval-Augmented Generation (RAG) Pipeline

This project implements a **Retrieval-Augmented Generation (RAG)** pipeline that retrieves relevant document chunks and combines them with large language model (LLM) reasoning to produce fact-based, source-grounded answers.
It demonstrates chunking, embedding, retrieval, and generation design choices tailored for mixed document types such as research papers, reports, and text files.

---

## Deliverables

* **Repository:** Full project folder
* **Language:** Python
* **Files Included:**

  * `document_loader.py` – Document preprocessing and chunking
  * `rag_pipeline.py` – Core retrieval and generation logic
  * `main.py` – usage file
  * `requirements.txt` – Dependency list
  * `.gitignore` – Environment and cache exclusion
  * `/docs` – Folder for sample source files (PDFs, TXT, DOCX)

---

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment

Add your GEMINI API key in `.env` (required by LLM provider).

### 3. Run the pipeline

```bash
python main.py
```

---

## Design Choices

### 1. **Chunking**

* For detailed documents like research papers, small chunks (around 256 tokens) don’t include enough context, so the model often can’t find complete answers, causing the LLM to respond with “Don’t have enough information”. For simpler text documents, this smaller size works fine. 

* Larger chunks give more context but also make processing slower and more expensive, since bigger chunks mean more tokens to handle, as multiple large chunks are combined as input during retrieval.


* To get a good balance between context and efficiency, we use a **chunk size of 512 tokens** with an **overlap of 64 tokens** in our setup.


### 2. **Embedding Model**

* `sentence-transformers/all-MiniLM-L6-v2`
* Selected for efficiency and strong semantic representation across mixed document types.

### 3. **Vector Database**

* **Chroma** is used as the vector store for embedding persistence and similarity search.

### 4. **Retrieval Strategy**

* **Top-k semantic similarity search** retrieves the most relevant document chunks.
* Retrieved chunks are concatenated and passed to the LLM as context for grounded response generation.

---

## Example Queries, Answers, and Sources

| # | Question                                                                         | Answer                                                                                                                                                                                                                                                                                                                                                                                                                                          | Sources                                                                                                                                                       |
| - | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **What problem does the attention mechanism solve in transformer architecture?** | The attention mechanism in Transformer architecture solves the problem where, in previous architectures like ConvS2S and ByteNet, the number of operations to relate signals from two arbitrary positions grew with distance, making it difficult to learn dependencies between distant positions. The Transformer reduces this to a constant number of operations.                                                                             | *Attention Is All You Need.pdf* — pages 2, 3, 5                                                                                                               |
| 2 | **How is FinTech transforming traditional banking services?**                    | FinTech is transforming traditional banking services by introducing online platforms, mobile apps, and automated services, which increase accessibility. Incumbent banks are adopting new technology, partnering with fintechs, and setting up new digital units, leading to a hyper-diversification of financial services. Banks are also becoming marketplaces, leveraging network effects and APIs to facilitate partnerships with fintechs. | *FinTech and the Future of Finance.pdf* — pages 31, 37; *banking_basics.txt*                                                                                  |
| 3 | **Mention two challenges of adopting AI in the banking sector.**                 | Two challenges of adopting AI in the banking sector are data privacy concerns and algorithmic bias.                                                                                                                                                                                                                                                                                                                                             | *Artificial Intelligence in Banking.docx*                                                                                                                     |
| 4 | **How does RAG reduce hallucination compared to parametric-only LLMs?**          | RAG reduces hallucination by incorporating a web search or document look-up process, which helps LLMs stick to the facts. This method prevents LLMs from describing non-existent policies or recommending non-existent legal cases.                                                                                                                                                                                                             | [Wikipedia — Retrieval-Augmented Generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)                                                    |
| 5 | **What is Chroma and how is it used as a vector database in LLM applications?**  | Don’t have enough information.                                                                                                                                                                                                                                                                                                                                                                                                                  | [Wikipedia — Retrieval-Augmented Generation](https://en.wikipedia.org/wiki/Retrieval-augmented_generation); *FinTech and the Future of Finance.pdf* — page 16 |

---

## Bonus Features Implemented

* ✅ **Source Citations** — Each generated answer includes clear reference sources for transparency.
* ✅ **Edge-Case Handling** — When no relevant context is found, the system gracefully outputs:

  > “Don’t have enough information.”


---

