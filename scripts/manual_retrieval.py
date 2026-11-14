from app.services.retrieval import retrieve_relevant_chunks
from app.services.vector_store import client


query = "What is Retrieval-Augmented Generation?"

try:
    results = retrieve_relevant_chunks(query=query, limit=5)

    print("\nUser Query:")
    print(query)

    print("\nRetrieved Chunks:")

    for result in results:
        print("\n-----------------------------")
        print("Filename:", result["filename"])
        print("Chunk Index:", result["chunk_index"])
        print("Similarity Score:", result["score"])
        print("Text:", result["chunk_text"])

finally:
    client.close()