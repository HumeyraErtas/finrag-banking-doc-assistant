# finrag-banking-doc-assistant

FinRAG — Banking Doc Assistant

Bu repo, bankacılık dokümanlarını (PDF) ingest edip parçalara ayıran, embedding üreten, FAISS tabanlı vektör araması yapan ve FastAPI + Streamlit ile demo/servis sağlayan bir RAG (Retrieval-Augmented Generation) prototipidir. Proje geliştiriciler için hazırlanmıştır: hızlı lokal geliştirme, değerlendirme (evaluation) ve üretime taşıma için gerekli bileşenleri içerir.

İçindekiler
- Quickstart (geliştirici)
- Ortam değişkenleri (önemli)
- Mimarî özet
- Geliştirme akışı
- Güvenlik ve gizli anahtarlar
- Katkıda bulunma

Hızlı Başlangıç (geliştirici)

1. Sanal ortam oluştur ve bağımlılıkları yükle

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Ortam dosyasını oluştur

```bash
cp .env.example .env   # Windows: copy .env.example .env
# sonra .env içindeki değerleri özelleştir
```

3. PDF'leri ekle

```text
mkdir -p data/pdfs
# banking PDF'lerinizi `data/pdfs/` içine koyun
```

4. Ingest (embedding + index oluşturma)

```bash
python scripts/ingest_cli.py
```

5. API çalıştırma (FastAPI)

```bash
uvicorn api.main:app --reload --port 8000
```

6. Streamlit demo

```bash
streamlit run streamlit_app.py
```

Önemli Ortam Değişkenleri
- `LLM_PROVIDER` — `openai` veya `ollama`
- `OPENAI_API_KEY` — OpenAI kullanıyorsanız kendi anahtarınız
- `OLLAMA_IMAGE`/ilgili ayarlar — Ollama ile lokal LLM çalıştırıyorsanız
- `DB_URL` / `DB_KEY` — varsa veri deposu bağlantı bilgileri
- `IDK_THRESHOLD` — cevap için "bilmiyorum" eşiği

Mimarî (kısa)
- `app/pdf_reader.py` — PDF'den metin çıkarma
- `app/chunking.py` — metinleri parçalara ayırma (chunking)
- `app/embeddings.py` — embedding üretimi (OpenAI/başka)
- `app/faiss_index.py` — FAISS index oluşturma ve sorgulama
- `api/main.py` — FastAPI uygulaması
- `streamlit_app.py` — demo arayüzü
- `scripts/ingest_cli.py` — ingest pipeline çalıştırma

Geliştirme Akışı
- Yeni bir özelliğe başlamadan önce issue/branch açın.
- Veri ingest değişiklikleri yaptıysanız `scripts/ingest_cli.py` ile tüm pipeline'ı yeniden çalıştırın.
- Lokal LLM ile test ediyorsanız `OLLAMA` veya `LLM_PROVIDER` ayarlarını güncelleyin.

Güvenlik ve Gizli Anahtarlar

- **ÖNEMLİ:** `OPENAI_API_KEY`, `DB_KEY` veya diğer gizli anahtarlar kasıtlı olarak repo'da placeholder veya boş bırakılmıştır. Her geliştirici/ci ortamı için bu anahtarlar ayrı ayrı sağlanmalıdır.
- `.env` dosyanızı asla versiyon kontrolüne (git) eklemeyin. `.gitignore` zaten bunu yapıyor; yine de kontrol edin.
- Prod ortamları için ortam değişkenleri dışında Azure Key Vault, AWS Secrets Manager, HashiCorp Vault gibi gizli yönetim servisleri kullanmanızı öneririz.
- Bu projenin herhangi bir paylaşılmış anahtar/credential ile çalıştırılması güvenlik riskleri doğurur; herkes kendi anahtarını kullanmalıdır.

Değerlendirme (Evaluation)
- `evaluation/eval_retrieval.py` ile retrieval kalite metriklerini (precision@k, recall@k) hesaplayabilirsiniz. Değerlendirme için `retrieval_gold` tablosunu/gold set'i doldurun.

Katkıda Bulunma
- Branch bazlı çalışma: `git checkout -b feat/your-feature`
- Kod kalitesi: existing style'a uyun, yeni bağımlılık ekliyorsanız `requirements.txt` güncelleyin.
- Test / değerlendirme ekleyin ve PR açıklamasında nasıl test edildiğini belirtin.

Lisans
- Bu repo [LICENSE](LICENSE) dosyasındaki şartlarla lisanslanmıştır.

İletişim
- Sorular/yardım için issue açabilirsiniz.

Docker

- Kısa: proje için basit bir Docker image oluşturup lokal veya CI ortamında çalıştırabilirsiniz.
- Örnek `Dockerfile` ile build ve run (projenin kök dizininde çalıştırın):

```bash
# image oluştur
docker build -t finrag-banking-doc-assistant:latest .

# .env dosyasını kullanarak container çalıştırma (gizli anahtarlar host'ta kalır)
docker run --env-file .env -p 8000:8000 finrag-banking-doc-assistant:latest
```

- Notlar:
	- `.env` dosyanızdaki `OPENAI_API_KEY` veya `DB_KEY` gibi gizli değerleri image içine gömmeyin. `--env-file` veya CI/CD secret mekanizmalarını kullanın.
	- Prod için Docker Compose veya Kubernetes ile gizli yönetimini entegre edin (Secret/KeyVault gibi).

## Güvenlik ve Gizli Anahtarlar

- **ÖNEMLİ:** `OPENAI_API_KEY`, `DB_KEY` gibi özel anahtarlar bilerek repo'da boş veya placeholder olarak bırakılmıştır. Güvenlik nedeniyle bu anahtarlar her geliştirici / kullanıcı için ayrı ayrı ayarlanmalıdır.
- **Yapılması gereken:** Kopyala `cp .env.example .env` veya Windows'ta `.env.example`'den `.env` oluşturup kendi değerlerinizi girin. Anahtarlarınızı asla versiyon kontrolüne dahil etmeyin.
- **Tavsiye:** Prod ortamları için ortam değişkenleri, gizli yönetim servisleri (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault vb.) veya CI/CD gizli değişkenleri kullanın. Lokal geliştirme için sadece kendi makinenizdeki `.env` dosyasını kullanın.

Bu değişiklik, kodu çalıştıracak herkesin kendi gizli anahtarlarını kullanmasını sağlamak içindir; paylaşılan veya ortak anahtar kullanmayınız.