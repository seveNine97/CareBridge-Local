# 🧠 Local Smart Assistant: Offline LLM Solution for Remote Areas

## ✨ Project Introduction

Welcome to **Local Smart Assistant**! This project is a large language model application specifically designed to address the issue of insufficient network infrastructure in remote areas. We leverage Google's latest **Gemma 3n model** combined with **Ollama offline service** to create an intelligent Q&A platform that runs entirely locally, without requiring an internet connection.

Our goal is to make knowledge accessible, empowering local communities by enabling users to obtain information and learn new things through a smart assistant, even in environments with poor network connectivity.

**Why choose it?**
- **100% Offline Operation**: All computations are performed locally, unaffected by network outages.
- **Local Knowledge Base Augmentation (RAG)**: Allows users to upload local documents, enabling the model to answer questions based on private data.
- **Multi-scenario Assistant Modes**: Built-in professional modes for various fields (e.g., agriculture, healthcare, education).
- **User-friendly Interface**: Built on Streamlit, intuitive and easy to use.

## 🌟 Key Highlights & Features

*   **Offline Large Language Model Chat**:
    *   Deeply integrated with the [Ollama](https://ollama.com/) platform, running the Gemma 3n model locally to provide a fast and smooth conversational experience.
    *   Users can interact with the model in natural language to get answers to various questions.
*   **Retrieval-Augmented Generation (RAG) Knowledge Base**:
    *   **Document Upload**: Supports uploading local documents in formats such as `TXT`, `MD`, `PDF`.
    *   **Intelligent Retrieval**: The application intelligently chunks, vectorizes, and stores document content in a local [ChromaDB](https://www.trychroma.com/) vector database.
    *   **Context Augmentation**: When a user asks a question, the system retrieves the most relevant document snippets from the knowledge base and passes them as additional context to the Gemma 3n model, ensuring accuracy and relevance of the answers.
    *   **Persistent Storage**: Knowledge base data persists even after the application is closed, eliminating the need for repeated uploads and processing.
*   **Dynamic Assistant Modes**:
    *   The sidebar provides several preset assistant modes, such as "Agricultural Expert," "Basic Medical Consultation," "Weather Disaster Warning," "Basic Education Knowledge," etc.
    *   Users can switch modes based on their needs, and the model will automatically adjust its answering style and focus to provide more professional services.
*   **Real-time User Experience Optimization**:
    *   **Streaming Response**: Model answers are displayed incrementally with a typewriter effect, providing a more natural interaction.
    *   **File Processing Progress Bar**: Clearly displays progress when uploading and processing knowledge documents, reducing user anxiety during waiting times.
    *   **Ollama Service and Model Status Check**: Intelligently detects whether the Ollama service is running and if the required models are downloaded, providing intuitive guidance and error prompts.
*   **Clean and Intuitive UI**:
    *   Built on the Streamlit framework, with a clear layout and easy operation.
    *   Supports practical functions such as adjusting model generation temperature and clearing chat history.

## 🛠️ Technology Stack

*   **Core Framework**: [Python](https://www.python.org/)
*   **Web Application Framework**: [Streamlit](https://streamlit.io/)
*   **Local LLM Service**: [Ollama](https://ollama.com/) (running Gemma 3n and nomic-embed-text)
*   **LLM Orchestration & RAG**: [LangChain](https://www.langchain.com/) (for document loading, text splitting, embedding, and vector store integration)
*   **Vector Database**: [ChromaDB](https://www.trychroma.com/) (local embedded vector database)
*   **PDF Parsing**: [PyPDF](https://pypdf.readthedocs.io/en/stable/)

## 🚀 Quick Start

### Prerequisites

Before running this project, please ensure your system meets the following requirements:

1.  **Python 3.8+**: Recommended to use [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) for environment management.
2.  **Git**: For cloning the project repository.
3.  **Ollama**: Visit [ollama.com](https://ollama.com/) to download and install the Ollama application for your operating system.

### Installation and Running

1.  **Clone the project repository:**
    ```bash
    git clone https://github.com/seveNine97/offline-gemma-assistant.git # Please replace with your actual repository name
    cd offline-gemma-assistant
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt # If you created requirements.txt
    # Or install manually:
    pip install streamlit ollama langchain langchain-community chromadb pypdf langchain-ollama langchain-chroma
    ```
    *(Suggestion: Run `pip freeze > requirements.txt` in the project root to generate `requirements.txt` for easier installation by others.)*

4.  **Start the Ollama service:**
    Run the following command in your terminal. The Ollama desktop application usually runs automatically in the background; if it's already running, no need to repeat.
    ```bash
    ollama serve
    ```

5.  **Download the large language model and embedding model:**
    These two models need to be downloaded once, after which they can be used offline.
    ```bash
    ollama pull gemma3n
    ollama pull nomic-embed-text
    ```

6.  **Run the Local Smart Assistant application:**
    From the project root directory (where `app.py` is located), run:
    ```bash
    streamlit run app.py
    ```
    Your default web browser will automatically open a new tab, displaying the "Local Smart Assistant" application.

## 💡 Usage Guide

*   **Chat Interaction**: Enter your question in the input box at the bottom, click "Send" or press Enter, and the model will provide an answer.
*   **Select Assistant Mode**: In the left sidebar, you can select different "Assistant Modes" (e.g., Agricultural Expert, Medical Consultation) to get professional answers tailored to specific domains.
*   **Knowledge Base (RAG)**:
    *   Click "Upload your knowledge documents (TXT, MD, PDF)" in the sidebar and select the local documents you want the model to learn from.
    *   After uploading, click the "Process Uploaded Files" button. The system will process the documents and build a local knowledge base.
    *   **Note**: PDF files must contain selectable text layers; scanned image PDFs may not allow text extraction.
    *   Once the knowledge base is built, the model will prioritize referring to these documents when answering relevant questions.
    *   Click the "Clear Knowledge Base" button to clear the index of all uploaded documents.
*   **Clear Chat History**: Click the "Clear Chat History" button in the sidebar to start a new conversation.
*   **Adjust Generation Temperature**: Use the slider in the sidebar to adjust the "Generation Temperature," controlling the randomness or determinism of the model's responses.

## 📂 Project Structure

```bash
kaggle_competition/
├── app.py # Main Streamlit application code
├── requirements.txt # Python dependencies list (recommended to create)
├── README.md # Project README file (this file)
├── chroma_db_rag/ # Folder for persistently storing RAG knowledge base data (automatically generated)
├── venv/ # Python virtual environment (locally created)
├── .gitignore # Git ignore file
```

## 🤝 Contributions

We welcome all developers interested in offline AI and technology empowerment for remote areas to join! If you have any ideas or suggestions, feel free to submit a Pull Request or create an Issue.

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙏 Acknowledgements

*   [Kaggle](https://www.kaggle.com/) and [Google](https://about.google/) for hosting the Gemma 3n Hackathon.
*   The [Ollama](https://ollama.com/) team for their outstanding contributions to local large language model services.
*   The [Streamlit](https://streamlit.io/) team for providing an excellent web application framework.
*   The [LangChain](https://www.langchain.com/) team for providing powerful tools for LLM application development.
*   The [ChromaDB](https://www.trychroma.com/) team for providing an easy-to-use vector database.
*   All contributors from the open-source community.
