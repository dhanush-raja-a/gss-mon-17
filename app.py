import streamlit as st
from langchain.document_loaders import WebBaseLoader

st.set_page_config(page_title="Simple Web Scraper", layout="wide")

st.title("LangChain Web Scraper — Minimal UI")
st.write("Enter a URL below and view scraped text using **WebBaseLoader** only.")

# --- URL Input Box (Center Large Box) ---
url = st.text_input("Enter URL to scrape", placeholder="https://example.com", label_visibility="visible")

# Button
scrape_btn = st.button("Scrape using LangChain WebBaseLoader")

# --- Scrape Logic ---
if scrape_btn:
    if not url.strip():
        st.error("Please enter a valid URL.")
    else:
        try:
            st.info("Scraping... Please wait")
            loader = WebBaseLoader(url.strip())
            docs = loader.load()

            if docs and docs[0].page_content:
                text = docs[0].page_content

                st.subheader("Scraped Text")
                st.text_area("", value=text, height=600)
                st.download_button("Download .txt", text, file_name="scraped.txt")
            else:
                st.warning("No text extracted. The website may block scraping or load content via JavaScript.")
        except Exception as e:
            st.error(f"Error occurred: {e}")
else:
    st.info("Enter a URL above and click Scrape to view text.")