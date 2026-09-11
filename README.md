# 🇮🇳 BIS AI Assistant

### AI-Powered Intelligent Assistant for Indian Standards and BIS Services

An AI-powered assistant designed to help **industries, consumers, and other users** discover and understand information related to **Bureau of Indian Standards (BIS)** standards, certification, licensing, testing, and consumer services.

The system combines **Retrieval-Augmented Generation (RAG)**, semantic search, multilingual support, and a modern web interface to provide grounded answers along with relevant document sources.

---

## 🚀 Live Demo

🌐 **Frontend:**  
https://sih-bis-assistant.vercel.app

⚙️ **Backend API:**  
https://sih-bis-assistant-gnh2.onrender.com

📚 **API Documentation:**  
https://sih-bis-assistant-gnh2.onrender.com/docs

> The backend is hosted on Render's free tier, so the first request after inactivity may take longer while the service wakes up.

---

# ✨ Features

## 🤖 AI-Powered Question Answering

Ask questions about BIS standards and services using natural language.

The assistant retrieves relevant information from the knowledge base before generating an answer.

---

## 🔎 Semantic Document Search

The system uses vector embeddings to find documents and passages that are semantically relevant to the user's question rather than relying only on keyword matching.

---

## 📚 Retrieval-Augmented Generation

The AI response is grounded in retrieved reference documents.

```text
User Question
      ↓
Question Processing
      ↓
Semantic Retrieval
      ↓
Relevant Document Chunks
      ↓
Context Construction
      ↓
LLM
      ↓
Grounded Answer + Sources
