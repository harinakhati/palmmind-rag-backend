from app.services.llm import generate_answer, client as gemini_client
from app.services.vector_store import client as qdrant_client
from app.services.retrieval import retrieve_relevant_chunks


query = "What is Retrieval-Augmented Generation?"

try:
    print("\nRetrieving relevant document chunks...")

    # Step 1: Retrieve chunks from Qdrant
    retrieved_chunks = retrieve_relevant_chunks(
        query=query,
        limit=3,
    )

    print("Retrieved chunks:", len(retrieved_chunks))

    # Step 2: Generate an answer using Gemini
    print("\nGenerating answer with Gemini...")

    answer = generate_answer(
        query=query,
        retrieved_chunks=retrieved_chunks,
    )

    # Step 3: Display the generated answer
    print("\n========== GENERATED ANSWER ==========")
    print(answer)

    print("\n========== SOURCES ==========")

    for chunk in retrieved_chunks:
        print(
            f"Filename: {chunk['filename']} | "
            f"Chunk: {chunk['chunk_index']} | "
            f"Score: {chunk['score']:.4f}"
        )

finally:
    qdrant_client.close()
    gemini_client.close()