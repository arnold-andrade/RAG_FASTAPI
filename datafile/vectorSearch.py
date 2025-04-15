from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
import vertexai
from PyPDF2 import PdfReader
import uuid
import nltk

nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

import os
from dotenv import load_dotenv

load_dotenv()

client = bigquery.Client.from_service_account_json(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

vertexai.init(project="carbon-beanbag-452610-q6", location="us-central1")

def split_text_into_chunks(text, max_chars=3000):
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks


def extract_pdf_by_chunks(pdf_path):
    reader = PdfReader(pdf_path)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text or not text.strip():
            continue
        small_chunks = split_text_into_chunks(text, max_chars=3000)
        for idx, chunk in enumerate(small_chunks):
            chunks.append({
                "content": chunk,
                "page_number": i + 1,
                "chunk_number": idx + 1
            })
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = TextEmbeddingModel.from_pretrained("text-embedding-005")
    inputs = [TextEmbeddingInput(t, "RETRIEVAL_DOCUMENT") for t in texts]
    embeddings = model.get_embeddings(inputs, output_dimensionality=256)
    return [e.values for e in embeddings]

def upload_safe(chunks, title, doc_id):
    if not chunks:
        return

    try:
        texts = [chunk['content'] for chunk in chunks]
        embeddings = embed_texts(texts)
        rows_to_insert = []

        for chunk, embedding in zip(chunks, embeddings):
            rows_to_insert.append({
                "content": chunk["content"],
                "title": title,
                "page_number": chunk["page_number"],
                "embedding": embedding,
                "doc_id": doc_id
            })

        table_id = "carbon-beanbag-452610-q6.testingdataset.relanto_doc"
        errors = client.insert_rows_json(table_id, rows_to_insert)
        if errors:
            print(f"❌ Error uploading batch to BigQuery: {errors}")
        else:
            print(f"✅ Uploaded batch of {len(rows_to_insert)} chunks.")

    except Exception as e:
        if len(chunks) == 1:
            print(f"❌ Cannot split further. Failed chunk: Page {chunks[0]['page_number']} - {e}")
        else:
            print(f"⚠️ Error: {e} — Splitting batch of {len(chunks)} into smaller parts")
            mid = len(chunks) // 2
            upload_safe(chunks[:mid], title, doc_id)
            upload_safe(chunks[mid:], title, doc_id)


def upload_to_bigquery(chunks, title="Untitled"):
    doc_id = str(uuid.uuid4())
    batch_size = 50  # Conservative batch size to start
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        upload_safe(batch, title, doc_id)


def get_content_from_bigquery(query):
    model = TextEmbeddingModel.from_pretrained("text-embedding-005")
    
    input_embedding = model.get_embeddings([
        TextEmbeddingInput(query, "RETRIEVAL_QUERY")
    ], output_dimensionality=256)[0].values


    embedding_str = ", ".join([str(val) for val in input_embedding])
    query_embedding = f"[{embedding_str}]"

    sql = f"""
    WITH query_embedding AS (
        SELECT [{embedding_str}] AS embedding
    ),
    exploded AS (
        SELECT
            doc.content,
            doc.title,
            doc.page_number,
            doc.embedding AS doc_embedding,
            query_embedding.embedding AS query_embedding,
            GENERATE_ARRAY(0, ARRAY_LENGTH(doc.embedding) - 1) AS idxs
        FROM `carbon-beanbag-452610-q6.testingdataset.relanto_doc` AS doc
        CROSS JOIN query_embedding
    ),
    distance_calc AS (
        SELECT
            content,
            title,
            page_number,
            SQRT(SUM(POW(doc_embedding[i], 2) - 2 * doc_embedding[i] * query_embedding[i] + POW(query_embedding[i], 2))) AS distance
        FROM exploded,
        UNNEST(idxs) AS i
        GROUP BY content, title, page_number
    )
    SELECT * FROM distance_calc
    ORDER BY distance ASC
    LIMIT 5;
    """

    query_job = client.query(sql)
    results = query_job.result()

    return [{
        "title": row.title,
        "page_number": row.page_number,
        "content": row.content,
        "distance": row.distance
    } for row in results]


if __name__ == "__main__":
    #pdf_path = r"C:\Users\Arnold Jerome\Downloads\Datasheets for Datasets.pdf"
    # title = "Relanto Employee Handbook"
    # chunks = extract_pdf_by_chunks(pdf_path)
    # upload_to_bigquery(chunks, title)
    # data=input("enter query:")
    
    results= get_content_from_bigquery(data)
    for i, row in enumerate(results, 1):
        print(f"\n🔹 Result {i}")
        print(f"Title: {row['title']}")
        print(f"Page: {row['page_number']}")
        print(f"Distance: {row['distance']:.4f}")
        print(f"Content:\n{row['content'][:1000]}...")



#embedding table query 
# CREATE TABLE `carbon-beanbag-452610-q6.testingdataset.relanto_doc` (
#   content STRING,
#   title STRING,
#   page_number INT64,
#   embedding ARRAY<FLOAT64>,
#   doc_id STRING
# );


#what are the different leave or holidays available to the employees