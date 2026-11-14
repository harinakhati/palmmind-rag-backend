from fastembed import TextEmbedding


# Initialize the embedding model
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

embedding_model = TextEmbedding(
    model_name=MODEL_NAME
)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate vector embeddings for a list of text chunks.
    """

    if not texts:
        return []

    embeddings = embedding_model.embed(texts)

    return [
        embedding.tolist()
        for embedding in embeddings
    ]