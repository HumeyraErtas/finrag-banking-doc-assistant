from __future__ import annotations
from dataclasses import dataclass
from app.retriever import Retriever, Retrieved
from app.llm import LLM
from app.config import settings


@dataclass
class Citation:
    chunk_id: int
    source_path: str
    title: str
    page_start: int
    page_end: int
    score: float
    snippet: str


@dataclass
class RAGResponse:
    answer: str
    citations: list[Citation]
    used_context: bool
    idk: bool
    top_score: float | None


def build_prompt(question: str, contexts: list[Retrieved]) -> str:
    # Keep prompt deterministic and citation-friendly
    context_blocks = []
    for i, c in enumerate(contexts, start=1):
        hdr = f"[KAYNAK {i}] file={c.source_path} pages={c.page_start}-{c.page_end} score={c.score:.3f}"
        body = c.text
        context_blocks.append(f"{hdr}\n{body}")
    joined = "\n\n".join(context_blocks)

    prompt = f"""
Aşağıdaki kaynak parçalarını (KAYNAK 1..N) kullanarak soruyu cevapla.
Kurallar:
- Yalnızca verilen kaynaklara dayan.
- Cevabın sonuna "Kaynaklar:" altında hangi KAYNAK numaralarını kullandığını yaz.
- Kaynaklar yetersizse açıkça "Bu dokümanlarda bulamadım" de.

Soru:
{question}

Kaynaklar:
{joined}
""".strip()
    return prompt


def to_citations(ctxs: list[Retrieved], max_citations: int = 5) -> list[Citation]:
    out = []
    for c in ctxs[:max_citations]:
        snippet = c.text[:300].replace("\n", " ").strip()
        out.append(
            Citation(
                chunk_id=c.chunk_id,
                source_path=c.source_path,
                title=c.title,
                page_start=c.page_start,
                page_end=c.page_end,
                score=c.score,
                snippet=snippet,
            )
        )
    return out


class RAG:
    def __init__(self, retriever: Retriever, llm: LLM):
        self.retriever = retriever
        self.llm = llm

    def answer(self, question: str) -> RAGResponse:
        ctxs = self.retriever.retrieve(question, top_k=settings.top_k)
        if not ctxs:
            return RAGResponse(
                answer="Bu dokümanlarda ilgili bilgi bulamadım.",
                citations=[],
                used_context=False,
                idk=True,
                top_score=None,
            )

        top_score = ctxs[0].score

        # "Bilmiyorum eşiği"
        if top_score < settings.idk_threshold:
            return RAGResponse(
                answer="Bu dokümanlarda sorunu güvenle yanıtlayacak yeterli bilgi bulamadım.",
                citations=to_citations(ctxs),
                used_context=True,
                idk=True,
                top_score=top_score,
            )

        prompt = build_prompt(question, ctxs)
        ans = self.llm.generate(prompt).strip()

        return RAGResponse(
            answer=ans,
            citations=to_citations(ctxs),
            used_context=True,
            idk=False,
            top_score=top_score,
        )
