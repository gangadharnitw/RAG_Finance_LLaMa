### Table of Contents
1. [Introduction](#introduction)
2. [Retrieval Augmented Generation RAG System](#retrieval-augmented-generation-rag-system)
3. [Data Collection](#data-collection)

## Introduction
[Back to top](#table-of-contents)

**Goal:**  
Create an AI assistant capable of analyzing financial reports and providing key investment insights, eliminating the need to manually review the reports every time.

**Approach Considerations:**  
I’ve explored two possible approaches:

1. **Approach 1:** Fine-tune an open-source LLM like LLaMA 3.2 with financial documents to embed domain-specific knowledge.
2. **Approach 2:** Use Retrieval-Augmented Generation (RAG) to enhance an LLM with external financial data sources.

**Reasons for Choosing RAG:**

- **Data Labeling Requirements:** Fine-tuning typically requires labeled data, which I don’t have access to.
- **Cost:** Fine-tuning can be resource-intensive, requiring multiple GPU hours, making it expensive.
- **Continuous Updates:** Every time new financial data becomes available, fine-tuning would need to be repeated. To avoid this, RAG allows dynamic updates by simply adjusting the knowledge base, eliminating the need for constant retraining.

Given these factors, I’ve decided to proceed with the RAG approach and focus on understanding its components to build a simple, efficient application.


## Retrieval Augmented Generation RAG system
[Back to top](#table-of-contents)

To build a Retrieval-Augmented Generation (RAG) system, you can follow these step-by-step processes. These steps cover everything from data preparation to deployment. 

### **Step 1: Data Collection**
   - **Objective:** Gather the knowledge base or corpus from which relevant information will be retrieved.
   - **Actions:**
     - Collect financial reports or documents in digital formats (PDFs, CSVs, Word docs, etc.).
     - Ensure you have a substantial corpus of data that covers a wide range of financial information and reports.

### **Step 2: Document Preprocessing**
   - **Objective:** Prepare the collected documents for efficient retrieval and chunking.
   - **Actions:**
     - **Text Extraction:** Extract text from various formats (PDF, CSV, DOCX) using libraries like `PyPDF2`, `pdfplumber`, or `docx`.
     - **Cleaning:** Clean the extracted text by removing unwanted characters, stopwords, and noise (e.g., headers, footers, watermarks).
     - **Document Segmentation (Chunking):** Split large documents into smaller, coherent sections based on paragraph structure, page breaks, or a fixed length of tokens (e.g., 500–1000 tokens per chunk).
     - **Metadata Addition (Optional):** Add metadata like document titles, dates, or keywords for easier retrieval.

### **Step 3: Indexing the Documents**
   - **Objective:** Create an index for efficient search and retrieval of relevant chunks of data.
   - **Actions:**
     - **Embedding Generation:** Convert the document chunks into dense vector embeddings using an embedding model like `Sentence-BERT`, `OpenAI Embeddings`, or similar.
     - **Indexing with a Vector Store:** Use a vector search library like FAISS, Pinecone, or Elasticsearch to store the embeddings. These allow for fast, semantic similarity searches.
     - **Index Metadata:** If you added metadata, ensure it is also indexed to provide more contextual or targeted search options.

### **Step 4: Embedding the Queries**
   - **Objective:** Enable the system to understand user queries semantically.
   - **Actions:**
     - **Query Preprocessing:** When a user submits a query, preprocess it to remove noise and ensure the query is in a usable format.
     - **Embedding the Query:** Use the same embedding model that you used for documents to convert the user’s query into a vector representation, ensuring consistent semantic comparison.

### **Step 5: Information Retrieval**
   - **Objective:** Retrieve the most relevant documents or document chunks based on the user query.
   - **Actions:**
     - **Similarity Search:** Perform a similarity search by comparing the query vector with the indexed document embeddings. The retrieval model will return the top `n` most relevant chunks (e.g., top 5).
     - **Optional Ranking or Filtering:** Apply additional ranking mechanisms to prioritize the most relevant or trustworthy sources. This can be done using techniques like TF-IDF or BM25 for additional precision.

### **Step 6: Feed Retrieved Documents to LLM**
   - **Objective:** Provide the language model with the retrieved documents to generate a well-informed response.
   - **Actions:**
     - **Format the Input:** Pass both the query and the retrieved document chunks to the language model (LLM) in a structured format, ensuring it can generate a response based on the retrieved information.
     - **Prompt Engineering:** Design effective prompts to ensure that the LLM uses the retrieved documents correctly. The prompt should ask the LLM to provide a concise, relevant answer based on the provided context.

### **Step 7: Answer Generation**
   - **Objective:** Generate a context-aware response using the LLM.
   - **Actions:**
     - The LLM processes both the user query and the retrieved document chunks.
     - It generates a human-like response that incorporates the key information from the retrieved documents, ensuring that the response is accurate and relevant to the query.

### **Step 8: Post-Processing (Optional)**
   - **Objective:** Enhance the generated output before presenting it to the user.
   - **Actions:**
     - **Answer Refinement:** Post-process the generated answer for formatting, completeness, or specific terminology (e.g., for financial jargon).
     - **Confidence Scoring:** Optionally calculate the confidence score of the generated response based on the relevance of the retrieved documents.
     - **Filtering:** Filter or truncate overly long or irrelevant content before delivering the final output.

### **Step 9: User Interface (UI)**
   - **Objective:** Create a frontend or interface for user interaction.
   - **Actions:**
     - Build a simple UI using frameworks like Streamlit, Flask, or any web-based application.
     - Allow users to input queries (such as asking for financial insights or report analysis) and view the generated answers.
     - Ensure the UI presents the generated answers clearly and allows users to interact further if needed (e.g., to ask follow-up questions).

### **Step 10: Feedback Loop and Continuous Learning (Optional)**
   - **Objective:** Improve the system’s performance over time by leveraging user feedback.
   - **Actions:**
     - **Feedback Collection:** Allow users to provide feedback on the relevance and quality of the answers.
     - **Fine-tuning or Adjustments:** Adjust the retrieval or generation components based on feedback, either by fine-tuning the retrieval algorithm, adjusting prompts, or improving document preprocessing.

### **Step 11: Evaluation and Metrics**
   - **Objective:** Measure and optimize the performance of the RAG system.
   - **Actions:**
     - Evaluate the quality of the generated responses using metrics such as BLEU, ROUGE, or manual human evaluation.
     - Measure retrieval accuracy by evaluating how well the retrieval system selects the most relevant documents for a query.
     - Continuously optimize the components based on evaluation metrics.

### **Step 12: Deployment**
   - **Objective:** Deploy the RAG system to production.
   - **Actions:**
     - Package the entire system (retrieval, LLM, UI) into a deployable app or service.
     - Use tools like Docker or Kubernetes for scaling if necessary.
     - Monitor system performance in real-time, ensuring it can handle user queries efficiently.

---

### **Recap of Key Components**
1. **Data Collection and Preprocessing:** Prepare the financial reports.
2. **Document Embedding and Indexing:** Generate embeddings and store them for fast retrieval.
3. **Query Embedding:** Convert user queries into vector representations.
4. **Retrieval Mechanism:** Retrieve relevant documents based on similarity search.
5. **LLM Integration:** Feed the retrieved documents into the LLM for response generation.
6. **UI and Feedback Loop:** Provide users with a platform to interact with the system and offer feedback.

---

### **Simple Example Workflow:**
1. User asks, "What was Apple's revenue growth last quarter?"
2. Query is embedded and compared with indexed financial report chunks.
3. The top 5 most relevant document chunks are retrieved from the knowledge base.
4. These chunks are passed to the LLM with a prompt like: "Based on the following data, what was Apple’s revenue growth last quarter?"
5. The LLM generates a response, which is displayed to the user.

By following these steps, you can build a robust RAG system that can dynamically answer user queries by retrieving relevant financial data and generating accurate insights using an LLM.


## Data collection
[Back to top](#table-of-contents)

#### SEC EDGAR 10-K Report Downloader and Parser (sec_edgar.py):
This script automates downloading and extracting specific sections from the SEC EDGAR `10-K` financial filings. It retrieves the CIK using a company's ticker, downloads the latest `10-K` reports, extracts specified sections, and saves them as JSON files.

**Script is tested to download and parse the latest ten 10-K filing reports of AAPL, QCOM, NVDA.**

### **1. Key Dependencies**
- `requests`: For making HTTP requests to SEC EDGAR.
- `BeautifulSoup`: For parsing HTML and XML content.
- `os`: For file and directory management.
- `datetime`, `re`, `json`: For date handling, regex parsing, and JSON file handling.

### **2. Main Components**

- **`sec_edgar_10k_reports(ticker, count, download_dir)`**: 
  Retrieves the CIK, fetches the latest `10-K` report URLs, and downloads them to a local directory.
  
- **`parse_and_extract_items(file_path, item_wishlist=None)`**: 
  Parses downloaded HTML reports and extracts specified sections (e.g., "Item 1", "Item 7"), returning them in a dictionary.

- **`extract_sec_10k_items(ticker, count=1)`**: 
  Automates downloading and parsing of `10-K` reports for a given ticker, saving extracted items to JSON files.

### **3. Example Usage**
```python
extract_sec_10k_items('AAPL', count=1)
```

This will download the latest `10-K` report for Apple, extract specific items, and save them in a JSON file.

### **4. Directory Structure**
- **`downloads/ticker`**: Stores downloaded HTML reports.
- **`downloads/ticker/json`**: Stores extracted sections in JSON format.

This script simplifies the process of downloading and analyzing financial filings from the SEC EDGAR database.