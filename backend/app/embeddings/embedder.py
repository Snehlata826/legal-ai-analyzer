from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS


class EmbeddingEngine:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def chunk(self, text):
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100
        )
        return splitter.split_text(text)

    def embed(self, chunks):
        return self.model.encode(chunks)

    def build_vector_db(self, chunks, vectors):
        db = FAISS.from_embeddings(
            embeddings=vectors,
            texts=chunks
        )
        return db
