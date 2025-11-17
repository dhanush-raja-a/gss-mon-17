import streamlit as st
import time
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from bs4 import BeautifulSoup

# Optional Playwright loader (only used if available)
try:
    from langchain.document_loaders import PlaywrightURLLoader
    PLAYWRIGHT_AVAILABLE = True
except Exception:
    PLAYWRIGHT_AVAILABLE = False

st.set_page_config(page_title="Robust Scraper + Splitter", layout="wide")
st.title("Robust LangChain Scraper → Splitter (fallbacks included)")
st.write("Tries WebBaseLoader → requests → Playwright, then partitions text into chunks.")

# Inputs
url = st.text_input("URL to scrape", value="https://www.gatewaysoftwaresolutions.com/softwaredevelopment/")
chunk_size = st.number_input("Chunk size (chars)", min_value=200, max_value=5000, value=1500, step=100)
chunk_overlap = st.number_input("Chunk overlap (chars)", min_value=0, max_value=1000, value=200, step=50)
timeout = st.number_input("Request timeout (seconds)", min_value=5, max_value=120, value=20, step=5)
use_playwright = st.checkbox("Allow Playwright fallback (runs a headless browser)", value=True)
start = st.button("Scrape & Split")

def split_text(full_text, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_text(full_text)

# Simple requests loader (fast for large static HTML)
def load_with_requests(url, ua=None, timeout=20):
    headers = {"User-Agent": ua or "robust-scraper/1.0"}
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text, resp

# Try WebBaseLoader
def try_webbaseloader(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    return docs

# Try Playwright loader (if available)
def try_playwright_loader(url):
    # PlaywrightURLLoader will run a browser and return Documents
    loader = PlaywrightURLLoader(urls=[url], remove_selectors=["script", "style"])
    docs = loader.load()
    return docs

if start:
    if not url.strip():
        st.error("Enter a valid URL")
    else:
        st.info("Starting scraping sequence (WebBaseLoader → requests → Playwright)")
        elapsed_start = time.time()
        docs = None
        html_text = None
        source = None

        # 1) WebBaseLoader
        try:
            with st.spinner("Trying WebBaseLoader..."):
                docs = try_webbaseloader(url)
            if docs and any(d.page_content.strip() for d in docs):
                source = "WebBaseLoader"
                st.success("WebBaseLoader succeeded")
        except Exception as e:
            st.warning(f"WebBaseLoader failed: {e}")

        # 2) requests fallback
        if not source:
            try:
                with st.spinner("Falling back to requests..."):
                    html_text, resp = load_with_requests(url, timeout=timeout)
                # parse with BeautifulSoup for visible text
                soup = BeautifulSoup(html_text, "html.parser")
                # get body text (more robust)
                body = soup.body.get_text(separator="\n\n", strip=True) if soup.body else soup.get_text(separator="\n\n", strip=True)
                if body and len(body.strip()) > 50:
                    source = "requests"
                    docs = [{"page_content": body}]  # make similar shape
                    st.success(f"requests succeeded (status {resp.status_code})")
                else:
                    st.warning("requests returned HTML but extracted body text is small/empty (likely JS-rendered).")
            except Exception as e:
                st.warning(f"requests failed: {e}")

        # 3) Playwright fallback (if allowed and available)
        if not source and use_playwright:
            if not PLAYWRIGHT_AVAILABLE:
                st.warning("Playwright loader not installed or langchain PlaywrightURLLoader not available.")
            else:
                try:
                    with st.spinner("Falling back to Playwright (headless browser)... this may take longer"):
                        docs = try_playwright_loader(url)
                    if docs and any(d.page_content.strip() for d in docs):
                        source = "playwright"
                        st.success("Playwright loader succeeded")
                    else:
                        st.warning("Playwright returned no text.")
                except Exception as e:
                    st.error(f"Playwright loader error: {e}")

        elapsed_total = round(time.time() - elapsed_start, 2)
        st.write(f"Elapsed (total): {elapsed_total}s")

        if not source or not docs:
            st.error("All loaders failed or returned no text. Check network, increase timeout, or try locally with playwright installed.")
        else:
            # Normalize docs list (if requests branch used a fake doc)
            if isinstance(docs, list) and hasattr(docs[0], "page_content"):
                full_text = "\n\n".join(d.page_content for d in docs if getattr(d, "page_content", "").strip())
            elif isinstance(docs, list) and isinstance(docs[0], dict) and "page_content" in docs[0]:
                full_text = "\n\n".join(d["page_content"] for d in docs)
            elif isinstance(docs, list) and isinstance(docs[0], str):
                full_text = "\n\n".join(docs)
            else:
                # fallback: try to extract attribute
                try:
                    full_text = "\n\n".join(getattr(d, "page_content", str(d)) for d in docs)
                except Exception:
                    full_text = ""

            if not full_text.strip():
                st.error("Loader claimed success but produced empty text.")
            else:
                st.success(f"Loaded text from: {source} — total chars: {len(full_text)}")
                with st.expander("Raw start of text (first 2000 chars)"):
                    st.code(full_text[:2000])

                # Split
                with st.spinner("Splitting text into chunks..."):
                    chunks = split_text(full_text, chunk_size, chunk_overlap)
                st.success(f"Split into {len(chunks)} chunks")

                st.metric("Chunks", len(chunks))
                preview_n = min(5, len(chunks))
                st.subheader(f"Preview first {preview_n} chunks")
                for i in range(preview_n):
                    st.markdown(f"**Chunk {i+1} — {len(chunks[i])} chars**")
                    st.code(chunks[i][:1000])

                # Download combined chunk file
                combined = "\n\n--- CHUNK BREAK ---\n\n".join(chunks)
                st.download_button("Download all chunks (.txt)", combined, file_name="chunks.txt")
                st.download_button("Download as JSON", str(chunks), file_name="chunks.json")