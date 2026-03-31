# Human Fulfillment Project

[![README in Chinese](https://img.shields.io/badge/README-%E4%B8%AD%E6%96%87-red?style=for-the-badge)](./README.zh-CN.md)
[![Project Vision](https://img.shields.io/badge/Project-Human%20Fulfillment%20Vision-black?style=for-the-badge)](./Human%20Fulfillment%20Project%EF%BC%88%E4%BA%BA%E7%B1%BB%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92%EF%BC%89%E9%A1%B9%E7%9B%AE%E8%AF%B4%E6%98%8E.md)
[![Status](https://img.shields.io/badge/status-local%20MVP-orange?style=for-the-badge)](https://github.com/saqierma-cyber/Human-Fulfillment-Project)
[![Python](https://img.shields.io/badge/python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.44-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MiniMax](https://img.shields.io/badge/LLM-MiniMax-5B5BD6?style=for-the-badge)](https://platform.minimaxi.com/)

## Project Vision

**Human Fulfillment Project** starts from a simple belief: one human life is short, but human wisdom is cumulative.  
Instead of letting each person repeat the same confusion, mistakes, and regrets from scratch, this project aims to gather the wisdom of the ancients, teachers, thinkers, and ordinary people across generations, then turn that accumulated experience into practical AI assistance for real-life decisions.

This repository is one open-source MVP component of that larger vision.  
It focuses on building a **local analysis agent** that reads a private knowledge base of Zeng Shiqiang-related books and uses that corpus to analyze workplace and family situations from his perspective.

Let's start with the simplest yet most striking perspective to understand the length of life — a human life is merely over 30,000 days. If we transform these 30,000 plus days into square grids the size of an A4 paper, with each grid representing one day, then: the grid for 30 years old is roughly in the first 1/3 of the paper, marking the end and precipitation of youth; the grid for 60 years old falls slightly behind the middle of the paper, carrying the experience and sweetness of half a lifetime; the grid for 90 years old approaches the end of the paper, engraving the completeness and relief of a whole life.

<img width="487" height="487" alt="ScreenShot_2026-03-31_144608_133" src="https://github.com/user-attachments/assets/d8427d8f-1983-4d66-af83-af4b6c37f79f" />

In this grid chart, the days that have passed are filled solid grids, each hiding the joys, regrets, confusion and growth we have personally experienced — unchangeable and irreversible; the unarrived future is blank grids, which seem to be full of infinite possibilities. However, for each individual, there is only one path in life — we can only know the answer behind by stepping through each blank grid personally.

Unfortunately, many times, we are repeating the path that our predecessors have taken: the pits that the ancients have already stepped on, the confusion they have experienced, and the wrong choices they have made, we still repeat the same mistakes because we are unaware; the regrets that should have been avoided, the opportunities that should have been seized, and the directions that should have been firm, we often miss in confusion, and when we look back, we can only regret endlessly.

An individual's life is too short. We can only live once in our life, with no room for trial and error, and no chance to start over. The era of artificial intelligence we are in has precisely given us a chance to break this limitation — since we can use technology to gather the experiences and wisdom of all human beings throughout history, why can't we use these nutrients accumulated over thousands of years to improve our own lives and make up for our shortcomings and imperfections?

This is the original intention of the Human Fulfillment Project: we do not pursue the ultimate unity of "eliminating individual estrangement and merging into one", but are committed to gathering the wisdom of the ancients, the insights of famous teachers and scholars, and the life experiences of ordinary people in all dynasties. We sort out, precipitate and empower these scattered pieces of wisdom to help each individual make clearer decisions and firmer choices at the key nodes of life.

It is said that behind every successful man stands a woman. The vision of the Human Fulfillment Project is: behind every successful person stands a group of wise humans. Every individual does not have to face the confusion and difficulties of life alone; every choice can be supported by the wisdom of all previous generations.

With the assistance of artificial intelligence, we no longer have to explore and try errors alone — in the future, behind each person, there can be a "think tank army" composed of the wisdom of all previous generations, escorting our lives.

Life cannot be repeated, but we can take fewer detours and leave fewer regrets with the wisdom of our predecessors; the life of an individual is limited, but the wisdom of human beings is infinite. The Human Fulfillment Project officially sets off at this moment.

- [Human Fulfillment Project（人类补完计划）项目说明](./Human%20Fulfillment%20Project%EF%BC%88%E4%BA%BA%E7%B1%BB%E8%A1%A5%E5%AE%8C%E8%AE%A1%E5%88%92%EF%BC%89%E9%A1%B9%E7%9B%AE%E8%AF%B4%E6%98%8E.md)

## What This Repository Is

This is a **local RAG-style analysis MVP** built around Zeng Shiqiang's works.

Given a user-described life event, the system attempts to:
- identify the theme of the event
- retrieve relevant passages from the local book corpus
- structure the people, relationships, causes, and tensions involved
- generate an analysis in Zeng Shiqiang's perspective
- predict likely next developments
- provide action suggestions with citations when possible

Current focus:
- workplace situations
- family relationship situations

## What Is Included in This Open-Source Version

This repository includes:
- backend service code
- Streamlit local UI
- document ingestion scripts
- OCR re-ingestion scripts
- database export/debug scripts
- prompt templates
- environment template
- project documentation

This repository does **not** include:
- your private ebook corpus
- generated local database exports
- local virtual environment
- private `.env`
- your real MiniMax API key

## Repository Structure

```text
Human-Fulfillment-Project/
├── app/                         # FastAPI backend
│   ├── api/                     # Chat/admin routes
│   ├── core/                    # Config and prompts
│   ├── db/                      # DB models and session
│   └── services/                # Parsing, OCR, retrieval, analysis
├── ui/                          # Streamlit local UI
├── scripts/                     # Import, OCR, export, debug scripts
├── prompts/                     # Prompt templates
├── data/                        # Data directory placeholder
├── docker-compose.yml           # PostgreSQL + pgvector
├── Dockerfile
├── requirements.txt
├── .env.example
├── README.md
└── README.zh-CN.md
```

## Technical Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI |
| Frontend | Streamlit |
| Database | PostgreSQL + pgvector |
| Document Parsing | PyMuPDF, ebooklib |
| OCR | pytesseract + local tesseract |
| LLM Integration | MiniMax via OpenAI-compatible SDK |
| Runtime | Python 3.12 |
| Local Infra | Docker Compose |

## How It Works

1. Parse local `PDF / EPUB / TXT` files.
2. OCR scanned PDFs when text extraction is insufficient.
3. Chunk documents into retrieval units.
4. Store metadata and chunks in PostgreSQL.
5. Classify user input by theme.
6. Retrieve relevant chunks from the local corpus.
7. Ask MiniMax for structured analysis.
8. Fall back to local rule-based analysis when model output is unusable.
9. Render the result in a local Streamlit interface.

## Current Project Status

- Local MVP is working.
- OCR re-ingestion pipeline is implemented.
- Database export to JSONL is implemented for inspection.
- MiniMax compatibility has been improved with `reasoning_split=True`.
- OpenAI-compatible client has been hardened with `trust_env=False`.
- UI supports structured analysis display for local testing.
- Embedding-based semantic retrieval is **not** enabled yet in this public version.

## Quick Start

### 1. Create your environment file

```bash
cp .env.example .env
```

Fill in your own MiniMax configuration in `.env`.

### 2. Start PostgreSQL

```bash
docker compose up -d
```

### 3. Create a Python 3.12 virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Optional: install OCR dependencies

```bash
brew install tesseract tesseract-lang
```

Then enable OCR in `.env`.

### 5. Ingest documents

```bash
python scripts/ingest_books.py
```

If scanned PDFs were previously imported as zero-chunk documents:

```bash
python scripts/reingest_zero_chunk_docs.py
```

### 6. Start the backend

```bash
uvicorn app.main:app --reload
```

### 7. Start the local UI

```bash
streamlit run ui/streamlit_app.py
```

## Suitable Questions

- workplace power and collaboration issues
- family conflicts with clear participants
- parent-child and intergenerational tension
- interpersonal communication and emotional management issues
- questions where cause, relationship, and decision tension are all explicit

## Not Suitable Questions

- highly abstract life-philosophy questions
- medical, legal, tax, or investment advice
- time-sensitive factual lookups
- questions without clear roles or conflict structure
- questions that require a fully general-purpose assistant

## Known Limitations

- Retrieval is still primarily keyword-driven in this version.
- Theme classification still depends on curated word patterns.
- Model-side structured output can fail and trigger fallback analysis.
- Citations are chunk-level, not strict paragraph-level references.
- Large anthology documents may still affect retrieval quality.
- The public repository does not include the actual book corpus.

## Roadmap

- improve theme coverage for family and workplace conflict patterns
- enable embedding-based semantic retrieval
- improve structured output success rate
- refine UI presentation
- improve citation precision
- build better evaluation cases for prompt and retrieval tuning

## Notes for Open-Source Use

- Bring your own legally obtained source documents.
- Bring your own MiniMax API key.
- This repository is designed for **local use first**, not public multi-user deployment.
- The included `.env.example` keeps configuration shape but does not expose private credentials.

