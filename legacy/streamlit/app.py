import streamlit as st
import ollama
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import tempfile
import shutil # For removing directory
# import time # 新增：用于引入延迟 # 移除此行

# --- Helper Function to Check Ollama Service ---
def is_ollama_running():
    try:
        ollama.list()
        return True
    except Exception:
        return False

# --- Language Management ---
# Define all text strings for translation
translations = {
    "en": {
        "page_title": "Local Smart Assistant",
        "app_title": "🧠 Your Local Smart Assistant",
        "app_description": "A completely offline assistant utilizing the **Gemma 3n model** running on your local device.\nInput any question or need, and it will do its best to assist you.",
        "divider": "---",
        "settings_sidebar_title": "Settings",
        "ollama_not_running_error": "❗ Ollama service is not running. Please start the service by typing `ollama serve` in the command line, otherwise the application will not work.",
        "select_model": "Select Model",
        "ollama_connection_warning": "Could not connect to Ollama service or get model list. Please ensure Ollama is running.",
        "model_not_downloaded_warning": "❗ Your selected model `{selected_model}` is not yet downloaded. Please run `ollama pull {selected_model}` in the command line.",
        "temperature_slider_label": "Generation Temperature (Temperature)",
        "temperature_slider_help": "Higher values will make the output more random, while lower values will make the output more focused and deterministic.",
        "clear_chat_history_button": "Clear Chat History",
        "assistant_mode_title": "Assistant Mode",
        "general_assistant_mode": "General Assistant",
        "general_assistant_instruction": "You are a helpful assistant. Please answer questions based on the provided context information (if any) and conversation history.",
        "agriculture_expert_mode": "Agriculture Expert",
        "agriculture_expert_instruction": "You are an experienced agricultural expert. Please provide professional advice on planting, pest and disease control, and yield optimization based on the provided crop knowledge and latest agricultural technologies. Your answers should be practical and easy to understand.",
        "basic_medical_consultation_mode": "Basic Medical Consultation",
        "basic_medical_consultation_instruction": "You are a basic medical information assistant. Please provide information on common health problems, disease prevention and basic first aid measures based on the provided medical knowledge. Please emphasize: you cannot replace professional medical diagnosis and treatment; all information is for reference only, and please seek medical attention promptly if you have health problems.",
        "weather_disaster_alert_mode": "Weather Disaster Alert",
        "weather_disaster_alert_instruction": "You are a weather and disaster alert assistant. Please provide weather forecasts, natural disaster (such as floods, earthquakes, landslides) warning information, and emergency response measures suggestions based on the provided meteorological data and disaster response knowledge. Emphasize timely attention to official warnings and evacuation notices.",
        "basic_education_knowledge_mode": "Basic Education Knowledge",
        "basic_education_knowledge_instruction": "You are a popularizer of basic education knowledge. Please explain various basic science, history, geography, and other knowledge in simple, clear language to help users learn and understand basic concepts.",
        "knowledge_base_rag_title": "Knowledge Base (RAG)",
        "rag_not_initialized_error": "Knowledge base not initialized or embedding model not ready, please check Ollama service and embedding model.",
        "knowledge_base_loaded_success": "Knowledge base loaded successfully!",
        "knowledge_base_init_failed": "Knowledge base initialization failed: {e}. Please ensure Ollama is running and the 'nomic-embed-text' model is downloaded.",
        "embedding_model_not_downloaded_warning": "❗ Embedding model `nomic-embed-text` is not yet downloaded. Please run `ollama pull nomic-embed-text` in the command line.",
        "unsupported_file_type_warning": "Unsupported file type: {file_extension}. Skipping {file_name}",
        "no_text_extracted_warning": "File {file_name} detected no text content or content is empty. Please ensure it is a selectable text PDF or a text file with content.",
        "file_loading_failed_error": "Failed to load file {file_name}: {e}",
        "loading_files_progress": "Loading files...",
        "processing_docs_progress": "Processing documents and building knowledge base...",
        "add_docs_failed_error": "Failed to add document batch to knowledge base: {e}",
        "docs_added_success": "Successfully added {num_splits} document blocks to the knowledge base.",
        "no_valid_text_blocks_warning": "No valid text blocks extracted from documents.",
        "no_docs_processed_info": "No documents processed.",
        "upload_docs_label": "Upload Your Knowledge Documents (TXT, MD, PDF)",
        "upload_docs_help": "Please upload documents containing selectable text. Scanned PDFs may not be able to extract text.",
        "process_uploaded_files_button": "Process Uploaded Files",
        "clear_knowledge_base_button": "Clear Knowledge Base",
        "clear_knowledge_base_success": "Knowledge base cleared!", # Updated message
        "clear_knowledge_base_failed": "Failed to clear knowledge base: {e}",
        "knowledge_base_empty_warning": "Knowledge base not initialized or already empty.",
        "offline_app_info": "💡 This is a completely offline application. All data processing is done on your local device and is not uploaded to any server.",
        "about_help_title": "About & Help",
        "version": "Version: 1.0.0",
        "author": "Author: [seveNine]",
        "introduction": "This is a completely offline local smart assistant, utilizing the Ollama platform to run Gemma 3n large language model, designed to provide intelligent conversation and knowledge retrieval services for users in environments with no or weak internet access.",
        "quick_start_title": "🚀 Quick Start:",
        "install_ollama": "1. **Install Ollama:** Visit `ollama.com` to download and install the Ollama application for your operating system.",
        "start_ollama_service": "2. **Start Ollama Service:** Open the command line and run `ollama serve`. The Ollama desktop application usually runs automatically in the background.",
        "download_models": "3. **Download Models:** In the command line, run `ollama pull gemma3n` (large language model) and `ollama pull nomic-embed-text` (knowledge base embedding model). These models need to be downloaded once and can then be used offline.",
        "run_app": "4. **Run This Application:** Locate the application's executable (e.g., `本地智慧助手.exe`) and double-click to run it.",
        "start_chat": "5. **Start Chat!**",
        "rag_usage_title": "📚 Knowledge Base (RAG) Usage:",
        "upload_docs_rag": "  * Click \"Upload Your Knowledge Documents\" to upload local files you want the model to learn from (currently supports TXT, MD, PDF).",
        "process_files_rag": "  * Click the \"Process Uploaded Files\" button, and the application will add the document content to the local knowledge base.",
        "pdf_note_rag": "    * **Note:** PDF files must contain a selectable text layer; scanned PDFs may not be able to extract content.",
        "model_retrieval_rag": "  * The model will prioritize retrieving relevant information from the knowledge base when answering questions.",
        "clear_db_rag": "  * The \"Clear Knowledge Base\" button will delete all uploaded document indexes but will not delete the original files.",
        "faq_title": "❓ Frequently Asked Questions:",
        "app_unresponsive_faq": "  * **App Unresponsive / Model Not Working:** Please ensure the Ollama service is running in the background, and you have downloaded the `gemma3n` and `nomic-embed-text` models.",
        "pdf_text_detection_faq": "  * **PDF File Not Detecting Text:** Please confirm that the PDF is text-selectable, not a scanned image.",
        "app_lagging_faq": "  * **App Lagging/Slow:** Model inference speed is limited by your computer's CPU performance. Choosing a smaller model or lowering the \"Generation Temperature\" may help.",
        "thank_you_note": "Thank you for using the Local Smart Assistant!",
        "chat_input_placeholder": "What questions do you have or what do you want to know?",
        "thinking_spinner": "Thinking... Please wait a moment, this depends on your CPU performance",
        "model_interaction_error": "An error occurred while interacting with the model: {e}",
        "ollama_service_check_warning": "Please ensure the Ollama service is running (type `ollama serve` in the command line) and you have downloaded your selected model (`ollama pull your_model_name`).",
        "language_switch_en": "English",
        "language_switch_zh": "中文",
        "select_assistant_mode": "Select Assistant Mode",
        "select_language": "Select Language / 选择语言",
        "restart_app_to_clear_message": "To fully clear the knowledge base files from disk, please restart the application."
    },
    "zh": {
        "page_title": "本地智慧助手",
        "app_title": "🧠 您的本地智慧助手",
        "app_description": "一个完全离线的助手，利用 **Gemma 3n 模型**在您的本地设备上运行。\n输入您的任何问题或需求，它将尽力为您提供帮助。",
        "divider": "---",
        "settings_sidebar_title": "设置",
        "ollama_not_running_error": "❗ Ollama 服务未运行。请在命令行中输入 `ollama serve` 启动服务，否则应用将无法工作。",
        "select_model": "选择模型",
        "ollama_connection_warning": "无法连接到 Ollama 服务或获取模型列表。请确保 Ollama 正在运行。",
        "model_not_downloaded_warning": "❗ 您选择的模型 `{selected_model}` 尚未下载。请在命令行中运行 `ollama pull {selected_model}`。",
        "temperature_slider_label": "生成温度 (Temperature)",
        "temperature_slider_help": "较高的值会使输出更随机，较低的值会使输出更集中和确定。",
        "clear_chat_history_button": "清空聊天记录",
        "assistant_mode_title": "助手模式",
        "general_assistant_mode": "通用助手",
        "general_assistant_instruction": "你是一个乐于助人的助手。请根据提供的上下文信息（如果提供）和对话历史来回答问题。",
        "agriculture_expert_mode": "农业专家",
        "agriculture_expert_instruction": "你是一个经验丰富的农业专家，请根据提供的农作物知识和最新农业技术，为用户提供专业的种植、病虫害防治和产量优化建议。你的回答应实用且易于理解。",
        "basic_medical_consultation_mode": "基础医疗咨询",
        "basic_medical_consultation_instruction": "你是一个基础医疗信息助手。请根据提供的医学知识，为用户提供常见的健康问题、疾病预防和基础急救措施信息。请务必强调：你不能替代专业的医生诊断和治疗，所有信息仅供参考，如有健康问题请及时就医。",
        "weather_disaster_alert_mode": "天气灾害预警",
        "weather_disaster_alert_instruction": "你是一个天气和灾害预警助手。请根据提供的气象数据和灾害应对知识，为用户提供天气预报、自然灾害（如洪水、地震、山体滑坡）的预警信息和紧急应对措施建议。强调及时关注官方预警和撤离通知。",
        "basic_education_knowledge_mode": "基础教育知识",
        "basic_education_knowledge_instruction": "你是一个基础教育知识普及者。请用简单、清晰的语言解释各种基础科学、历史、地理等知识，帮助用户学习和理解基础概念。",
        "knowledge_base_rag_title": "知识库 (RAG)",
        "rag_not_initialized_error": "知识库未初始化或嵌入模型未准备好，请检查 Ollama 服务和嵌入模型。",
        "knowledge_base_loaded_success": "知识库加载成功！",
        "knowledge_base_init_failed": "知识库初始化失败: {e}. 请确保 Ollama 正在运行且 'nomic-embed-text' 模型已下载。",
        "embedding_model_not_downloaded_warning": "❗ 嵌入模型 `nomic-embed-text` 尚未下载。请在命令行中运行 `ollama pull nomic-embed-text`。",
        "unsupported_file_type_warning": "不支持的文件类型: {file_extension}。跳过 {file_name}",
        "no_text_extracted_warning": "文件 {file_name} 未检测到任何文本内容或内容为空白。请确保是可选择文本的PDF或有内容的文本文件。",
        "file_loading_failed_error": "加载文件 {file_name} 失败: {e}",
        "loading_files_progress": "正在加载文件...",
        "processing_docs_progress": "正在处理文档并构建知识库...",
        "add_docs_failed_error": "将文档批次添加到知识库失败: {e}",
        "docs_added_success": "成功将 {num_splits} 个文档块添加到知识库。",
        "no_valid_text_blocks_warning": "未从文档中提取到任何有效文本块。",
        "no_docs_processed_info": "未处理任何文档。",
        "upload_docs_label": "上传您的知识文档 (TXT, MD, PDF)",
        "upload_docs_help": "请上传包含可选择文本的文档。扫描版PDF可能无法提取文本。",
        "process_uploaded_files_button": "处理上传文件",
        "clear_knowledge_base_button": "清除知识库",
        "clear_knowledge_base_success": "知识库已清空！", # Updated message
        "clear_knowledge_base_failed": "清空知识库失败: {e}",
        "knowledge_base_empty_warning": "知识库未初始化或已为空。",
        "offline_app_info": "💡 这是一个完全离线的应用。所有数据处理都在您的本地设备上完成，不会上传到任何服务器。",
        "about_help_title": "关于 & 帮助",
        "version": "版本: 1.0.0",
        "author": "作者: [seveNine]",
        "introduction": "这是一个完全离线的本地智慧助手，利用 Ollama 平台运行 Gemma 3n 大语言模型，旨在为无网络或弱网络环境的用户提供智能对话和知识检索服务。",
        "quick_start_title": "🚀 快速开始：",
        "install_ollama": "1. **安装 Ollama：** 访问 `ollama.com` 下载并安装适用于您操作系统的 Ollama 应用程序。",
        "start_ollama_service": "2. **启动 Ollama 服务：** 打开命令行，运行 `ollama serve`。Ollama 桌面应用通常会自动在后台运行。",
        "download_models": "3. **下载模型：** 在命令行中运行 `ollama pull gemma3n` (大语言模型) 和 `ollama pull nomic-embed-text` (知识库嵌入模型)。这些模型需要一次性下载，之后即可离线使用。",
        "run_app": "4. **运行本应用：** 找到本应用的启动程序 (例如：`本地智慧助手.exe`) 双击运行。",
        "start_chat": "5. **开始对话！**",
        "rag_usage_title": "📚 知识库 (RAG) 使用：",
        "upload_docs_rag": "  * 点击\"上传您的知识文档\"上传您想让模型学习的本地文件 (目前支持 TXT, MD, PDF)。",
        "process_files_rag": "  * 点击\"处理上传文件\"按钮，应用会将文档内容添加到本地知识库。",
        "pdf_note_rag": "    * **注意：** PDF 文件必须包含可选择的文本层，扫描版 PDF 可能无法提取内容。",
        "model_retrieval_rag": "  * 模型在回答问题时会优先从知识库中检索相关信息。",
        "clear_db_rag": "  * \"清除知识库\"按钮会删除所有已上传文档的索引，但不会删除原始文件。",
        "faq_title": "❓ 常见问题：",
        "app_unresponsive_faq": "  * **应用无响应 / 模型不工作：** 请确保 Ollama 服务正在后台运行，并且您已下载了 `gemma3n` 和 `nomic-embed-text` 模型。",
        "pdf_text_detection_faq": "  * **PDF 文件未检测到文本：** 请确认 PDF 是可选择文本的，而非图片扫描件。",
        "app_lagging_faq": "  * **应用卡顿/速度慢：** 模型推理速度受限于您电脑的CPU性能。选择较小的模型或降低\"生成温度\"可能有所帮助。",
        "thank_you_note": "感谢您使用本地智慧助手！",
        "chat_input_placeholder": "您有什么问题或想了解的？",
        "thinking_spinner": "思考中... 请稍候片刻，这取决于您的CPU性能",
        "model_interaction_error": "与模型交互时发生错误: {e}",
        "ollama_service_check_warning": "请确保 Ollama 服务正在运行 (在命令行中输入 `ollama serve`) 并且您已下载了您选择的模型 (`ollama pull your_model_name`)。",
        "language_switch_en": "English",
        "language_switch_zh": "中文",
        "select_assistant_mode": "Select Assistant Mode",
        "select_language": "Select Language / 选择语言",
        "restart_app_to_clear_message": "To fully clear the knowledge base files from disk, please restart the application."
    }
}

if "language" not in st.session_state:
    st.session_state.language = "en" # Default language is English

def get_text(key):
    return translations[st.session_state.language].get(key, str(key))


# --- Streamlit UI Configuration ---
st.set_page_config(
    page_title=get_text("page_title"),
    page_icon="🧠",
    layout="centered"
)

st.title(get_text("app_title"))
st.markdown(get_text("app_description"))

st.divider() # Adds a visual separator

# --- Sidebar for Settings ---
st.sidebar.title(get_text("settings_sidebar_title"))

# Language selection at the very top of sidebar
language_options = {
    get_text("language_switch_en"): "en",
    get_text("language_switch_zh"): "zh"
}
selected_display_language = st.sidebar.radio(
    get_text("select_language"),
    list(language_options.keys()),
    index=list(language_options.values()).index(st.session_state.language)
)

if language_options[selected_display_language] != st.session_state.language:
    st.session_state.language = language_options[selected_display_language]
    st.rerun()


# Check Ollama service status early
if not is_ollama_running():
    st.error(get_text("ollama_not_running_error"))
    st.stop() # Stop app execution if Ollama is not running

# Model selection
available_models = ["gemma3n:latest"] # Default model
try:
    ollama_models = ollama.list()['models']
    for model_info in ollama_models:
        if model_info['model'] not in available_models:
            available_models.append(model_info['model'])
except Exception:
    st.sidebar.warning(get_text("ollama_connection_warning"))

selected_model = st.sidebar.selectbox(get_text("select_model"), available_models)

# Validate if selected model is available
if selected_model not in [m['model'] for m in ollama.list()['models']]:
    st.warning(get_text("model_not_downloaded_warning").format(selected_model=selected_model))


# Temperature slider for model response creativity
temperature = st.sidebar.slider(get_text("temperature_slider_label"), 0.0, 1.0, 0.7, 0.05,
                                help=get_text("temperature_slider_help"))

# Clear chat history button
if st.sidebar.button(get_text("clear_chat_history_button")):
    st.session_state.messages = []
    st.rerun() # Rerun the app to clear displayed messages

# --- Dynamic System Instruction Mode ---
st.sidebar.markdown(get_text("divider") + "\n**" + get_text("assistant_mode_title") + "**")
scenario_modes = {
    get_text("general_assistant_mode"): get_text("general_assistant_instruction"),
    get_text("agriculture_expert_mode"): get_text("agriculture_expert_instruction"),
    get_text("basic_medical_consultation_mode"): get_text("basic_medical_consultation_instruction"),
    get_text("weather_disaster_alert_mode"): get_text("weather_disaster_alert_instruction"),
    get_text("basic_education_knowledge_mode"): get_text("basic_education_knowledge_instruction")
}
selected_mode = st.sidebar.selectbox(get_text("select_assistant_mode"), list(scenario_modes.keys()))
system_instruction = scenario_modes[selected_mode]


st.sidebar.markdown(get_text("divider") + "\n**" + get_text("knowledge_base_rag_title") + "**")

# --- RAG Specific Configuration and Functions ---
# Persistent directory for ChromaDB
# This will create a 'chroma_db_rag' folder next to app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
PERSIST_DIRECTORY = os.path.join(current_dir, "chroma_db_rag")

if "vectorstore" not in st.session_state:
    st.session_state.chroma_db_dir = PERSIST_DIRECTORY
    if not os.path.exists(st.session_state.chroma_db_dir):
        os.makedirs(st.session_state.chroma_db_dir)
    
    # Initialize Ollama Embeddings
    try:
        st.session_state.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        # Check if nomic-embed-text is actually pulled
        if "nomic-embed-text:latest" not in [m['model'] for m in ollama.list()['models']]:
            st.warning(get_text("embedding_model_not_downloaded_warning"))
            st.session_state.embeddings = None # Disable RAG if embedder is not ready
        else:
            st.session_state.vectorstore = Chroma(
                embedding_function=st.session_state.embeddings,
                persist_directory=st.session_state.chroma_db_dir
            )
            st.sidebar.success(get_text("knowledge_base_loaded_success"))
    except Exception as e:
        st.sidebar.error(f"{get_text('knowledge_base_init_failed').format(e=e)}. "
                         f"{get_text('restart_app_to_clear_message')}") # Add restart hint here too
        st.session_state.embeddings = None
        st.session_state.vectorstore = None


def process_documents(uploaded_files):
    if st.session_state.vectorstore is None:
        st.error(get_text("rag_not_initialized_error"))
        return

    documents = []
    
    # Progress bar for file loading
    loading_progress_bar = st.sidebar.progress(0, text=get_text("loading_files_progress"))
    
    for i, uploaded_file in enumerate(uploaded_files):
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            if file_extension == ".pdf":
                loader = PyPDFLoader(tmp_file_path)
            elif file_extension == ".txt" or file_extension == ".md":
                loader = TextLoader(tmp_file_path, encoding="utf-8")
            else:
                st.warning(get_text("unsupported_file_type_warning").format(file_extension=file_extension, file_name=uploaded_file.name))
                continue
            
            docs = loader.load()
            if not docs or not any(d.page_content.strip() for d in docs): # Check if any content is extracted
                st.warning(get_text("no_text_extracted_warning").format(file_name=uploaded_file.name))
            documents.extend(docs)
        except Exception as e:
            st.error(get_text("file_loading_failed_error").format(file_name=uploaded_file.name, e=e))
        finally:
            os.remove(tmp_file_path) # Clean up temp file
        
        loading_progress_bar.progress((i + 1) / len(uploaded_files), text=get_text("loading_files_progress") + f" {i+1}/{len(uploaded_files)}...")
    
    loading_progress_bar.empty() # Clear loading progress bar

    if documents:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(documents)
        
        if splits:
            # Progress bar for embedding and adding to vectorstore
            embedding_progress_bar = st.sidebar.progress(0, text=get_text("processing_docs_progress"))
            total_splits = len(splits)
            
            # Add documents in batches to show progress
            batch_size = 20 # Adjust batch size based on memory
            for i in range(0, total_splits, batch_size):
                batch_splits = splits[i:min(i + batch_size, total_splits)]
                try:
                    st.session_state.vectorstore.add_documents(batch_splits)
                except Exception as e:
                    st.error(get_text("add_docs_failed_error").format(e=e))
                    break # Stop if a batch fails
                
                progress = (i + len(batch_splits)) / total_splits
                embedding_progress_bar.progress(progress, text=get_text("processing_docs_progress") + f": {int(progress*100)}%")
            
            # st.session_state.vectorstore.persist() # Save changes to disk # 移除此行
            embedding_progress_bar.empty() # Clear embedding progress bar
            st.success(get_text("docs_added_success").format(num_splits=len(splits)))
        else:
            st.warning(get_text("no_valid_text_blocks_warning"))
    else:
        st.info(get_text("no_docs_processed_info"))


uploaded_files = st.sidebar.file_uploader(
    get_text("upload_docs_label"),
    type=["txt", "md", "pdf"],
    accept_multiple_files=True,
    help=get_text("upload_docs_help")
)

if uploaded_files:
    if st.sidebar.button(get_text("process_uploaded_files_button"), key="process_files_btn"):
        process_documents(uploaded_files)

# Clear ChromaDB persistent directory as well
if st.sidebar.button(get_text("clear_knowledge_base_button"), key="clear_db_btn"):
    if st.session_state.vectorstore:
        try:
            st.session_state.vectorstore.delete_collection() # Deletes all data in the collection
            
            # 关键修改：不再尝试显式删除目录，而是告知用户重启应用
            # 确保对象引用被释放
            st.session_state.vectorstore = None 
            
            st.success(get_text("clear_knowledge_base_success"))
            st.warning(get_text("restart_app_to_clear_message")) # 新增提示

            # 重新初始化向量存储（仅当嵌入模型可用且目录存在时）
            # 注意：此处不再检查目录是否被占用，因为物理删除不再是此逻辑的一部分。
            if st.session_state.embeddings and os.path.exists(PERSIST_DIRECTORY):
                st.session_state.vectorstore = Chroma(
                    embedding_function=st.session_state.embeddings,
                    persist_directory=st.session_state.chroma_db_dir
                )
            elif not os.path.exists(PERSIST_DIRECTORY): # 如果目录不存在，但成功清空了集合，则重新创建目录
                 os.makedirs(PERSIST_DIRECTORY)

        except Exception as e:
            st.error(f"{get_text('clear_knowledge_base_failed').format(e=e)}. "
                     f"{get_text('restart_app_to_clear_message')}") # 使用新的消息键
            st.session_state.vectorstore = None # 确保在任何错误时都将vectorstore设置为None
    else:
        st.warning(get_text("knowledge_base_empty_warning"))


st.sidebar.markdown(get_text("divider") + "\n")
st.sidebar.info(get_text("offline_app_info"))


# --- "About" / Help Section ---
with st.sidebar.expander(get_text("about_help_title")):
    st.markdown(f"""
    **{get_text("version")}**
    **{get_text("author")}**
    **{get_text("introduction")}**

    **{get_text("quick_start_title")}**
    1.  **{get_text("install_ollama")}**
    2.  **{get_text("start_ollama_service")}**
    3.  **{get_text("download_models")}**
    4.  **{get_text("run_app")}**
    5.  **{get_text("start_chat")}**

    **{get_text("rag_usage_title")}**
    *   {get_text("upload_docs_rag")}
    *   {get_text("process_files_rag")}
        *   **{get_text("pdf_note_rag")}**
    *   {get_text("model_retrieval_rag")}
    *   {get_text("clear_db_rag")}

    **{get_text("faq_title")}**
    *   {get_text("app_unresponsive_faq")}
    *   {get_text("pdf_text_detection_faq")}
    *   {get_text("app_lagging_faq")}

    **{get_text("thank_you_note")}**
    """)


# --- Initialize Session State (to store conversation history) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Previous Messages ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input(get_text("chat_input_placeholder")):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display a loading spinner while waiting for response
    with st.chat_message("assistant"):
        # Create a placeholder for streaming response
        message_placeholder = st.empty()
        full_response = ""
        with st.spinner(get_text("thinking_spinner")):
            try:
                # Call Ollama API to get response from selected model
                stream = ollama.chat(
                    model=selected_model, # Use the selected model from sidebar
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True, # Enable streaming responses
                    options=dict(temperature=temperature) # Apply temperature setting
                )

                for chunk in stream:
                    if 'content' in chunk['message']:
                        full_response += chunk['message']['content']
                        # Update the placeholder with the current full response and a blinking cursor
                        message_placeholder.markdown(full_response + "▌")
                # After streaming is complete, display the final response without the cursor
                message_placeholder.markdown(full_response)

                # Add assistant message to chat history
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"{get_text('model_interaction_error').format(e=e)}. "
                         f"{get_text('ollama_service_check_warning')}") # This already has a suggestion.

st.divider() # Another visual separator