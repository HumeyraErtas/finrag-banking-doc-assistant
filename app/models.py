from sqlalchemy import String, Integer, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_path: Mapped[str] = mapped_column(String(512), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(256), default="")

    chunks: Mapped[list["Chunk"]] = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_index", name="uq_doc_chunkindex"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), index=True)

    chunk_index: Mapped[int] = mapped_column(Integer)
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int] = mapped_column(Integer)

    text: Mapped[str] = mapped_column(Text)

    # FAISS stores vectors externally; we keep row alignment via "vector_id"
    vector_id: Mapped[int] = mapped_column(Integer, index=True)

    document: Mapped["Document"] = relationship("Document", back_populates="chunks")


class RetrievalGold(Base):
    """
    Optional: evaluation set (query -> relevant chunk ids)
    """
    __tablename__ = "retrieval_gold"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    query: Mapped[str] = mapped_column(Text)
    relevant_chunk_ids_csv: Mapped[str] = mapped_column(Text)  # "12,15,88"
