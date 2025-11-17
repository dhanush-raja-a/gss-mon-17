# Inter-GSS Web Scraper

This project is a **Streamlit-based web scraping tool** built using **LangChain**, with optional fallbacks (requests, BeautifulSoup, and Playwright). It allows you to:

- Enter any URL
- Extract page content (including large pages)
- Split the extracted content into text chunks
- Download the scraped result
- Debug loading issues (timeouts, JS-heavy pages)

---

## 🚀 Features

### ✔ LangChain `WebBaseLoader`

Primary loader for fast text extraction.

### ✔ Fallback Loaders

- **Requests + BeautifulSoup** for static HTML
- **Playwright** for JS-heavy websites

### ✔ Chunking Support

Uses `RecursiveCharacterTextSplitter`:

- Adjustable chunk size
- Adjustable chunk overlap
- Supports long documents

### ✔ Streamlit UI

Simple UI with:

- URL input box
- Scrape button
- Text output
- Chunk previews
- Download buttons

---

## 📦 Tech Stack

- **Python 3.10+**
- **Streamlit** for UI
- **LangChain** for loaders
- **Requests + BeautifulSoup** fallback
- **Playwright** for dynamic content

---

## 📚 Installation

### 1. Clone the repo

```bash
cd inter-gss
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If Playwright is enabled, install browsers:

```bash
python -m playwright install
```

---

## ▶️ Running the App

```bash
streamlit run app.py
```

Then open in browser:

```
http://localhost:8501
```

---

## 📖 How It Works

1. User enters a URL.
2. App tries loading using LangChain's `WebBaseLoader`.
3. If it fails, tries requests → BeautifulSoup.
4. If the site is JS-heavy, uses Playwright (if enabled).
5. Extracted content is split into chunks.
6. User can preview and download results.

---

## 🧩 File Structure

```
inter-gss/
├── app.py              # Streamlit main app
├── README.md           # Project documentation
├── requirements.txt    # Dependencies
└── ...                 # Other files
```

---

## 🛠 Future Improvements

- Vector search on chunks
- Database storage for scraped pages
- LLM summarization for large pages
- Multi-URL batch scraping

---

## 👨‍💻 Author

**Dhanush Raja A**

For improvements or additions, feel free to update the repository.
