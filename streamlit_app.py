import os
import requests
import streamlit as st

API_URL = st.sidebar.text_input("API URL", value="http://localhost:8000")

st.title("FinRAG – Bankacılık Dokümanları için RAG Asistanı")

q = st.text_area("Soru", height=120, placeholder="Örn: Ücret ve komisyon iade şartları nelerdir?")
ask = st.button("Sor")

if ask:
    if not q.strip():
        st.warning("Lütfen bir soru girin.")
    else:
        with st.spinner("Yanıt aranıyor..."):
            r = requests.post(f"{API_URL}/ask", json={"question": q}, timeout=120)
            if r.status_code != 200:
                st.error(f"API error: {r.status_code}\n{r.text}")
            else:
                data = r.json()
                st.subheader("Yanıt")
                st.write(data["answer"])

                st.caption(f"idk={data['idk']} | top_score={data.get('top_score')}")
                st.subheader("Kaynaklar (Citations)")
                for i, c in enumerate(data["citations"], start=1):
                    st.markdown(
                        f"""
**{i}. {os.path.basename(c['source_path'])}** (s. {c['page_start']}-{c['page_end']})  
Skor: {c['score']:.3f} | chunk_id: {c['chunk_id']}  
> {c['snippet']}
"""
                    )
