# PrivAI Sample Dataset

This folder contains a minimal demo dataset for the PrivAI MVP.

## Files
- `students.csv` — Columns: `id, name, fees_paid, semester`
- `marks.csv` — Columns: `id, subject, marks, exam`
- `feedback.csv` — Columns: `id, year, category, feedback_text`
- `policies.pdf` — Academic policies (2–3 pages)
- `NAAC_criteria.pdf` — NAAC criteria summary (2–3 pages)
- `sample_queries.txt` — Ready-to-run demo questions
- `generate_pdfs.py` — Script to generate PDFs if missing

## Generate PDFs (if not present)
```bash
cd samples
python generate_pdfs.py
```
Outputs: `policies.pdf`, `NAAC_criteria.pdf`

## How to Use with Backend
1) Start the backend (simplified)
```bash
cd backend
python -m app.main_simple
```

2) Upload CSVs and PDFs via API or UI
- API (example using curl):
```bash
# students.csv
curl -F "file=@samples/students.csv" http://localhost:8000/upload/
# marks.csv
curl -F "file=@samples/marks.csv" http://localhost:8000/upload/
# feedback.csv
curl -F "file=@samples/feedback.csv" http://localhost:8000/upload/
# policies.pdf
curl -F "file=@samples/policies.pdf" http://localhost:8000/upload/
# NAAC_criteria.pdf
curl -F "file=@samples/NAAC_criteria.pdf" http://localhost:8000/upload/
```

3) Trigger ingestion
```bash
curl -X POST http://localhost:8000/ingest/
```
Response includes number of chunks processed.

4) Ask queries (see `sample_queries.txt`)
```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Content-Type: application/json" \
  -d '{"query": "List students with unpaid fees this semester"}'
```

## Sample Queries
- List students with unpaid fees this semester
- Summarize placement feedback 2024
- Generate NAAC report summary for criteria X
- List top 10 students by marks in CS
- Summarize student complaints in last semester

## Notes
- The simplified backend returns mock answers but preserves metadata and sources for demonstration.
- For full RAG behavior, enable the full pipeline and install additional dependencies (`faiss-cpu`, `sentence-transformers`).
- CSVs are small and designed for quick ingest; PDFs are multi-page text for chunking.
