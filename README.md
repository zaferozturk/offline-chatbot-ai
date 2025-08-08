# 🧠 Offline AI Chatbot with LLaMA & Facebook BART

This project is an **offline AI-powered chatbot** built with **LLaMA 3.2 1B** and **Facebook BART Large MNLI** models.  
It provides a user-friendly **Streamlit web interface** and runs entirely without an internet connection.  
The application is containerized with **Docker** for easy deployment.

---

## 🚀 Features
- **Fully offline operation** — no internet required after setup.
- **Dual model integration**:  
  - **LLaMA 3.2 1B** → Natural language generation  
  - **Facebook BART Large MNLI** → Natural language inference and text classification
- **Streamlit-based modern chat interface**
- **Docker support** for quick setup and deployment
- **MCP Server integration** for multi-component coordination
- Built for **Python 3.12.9**

---

## 🛠 Tech Stack
- **Python 3.12.9**
- **[Ollama](https://ollama.ai/)** (for running LLaMA)
- **Facebook BART Large MNLI**
- **Streamlit**
- **Docker**
- **MCP Server**

---

## 📦 Installation

### 1️⃣ Clone the repository
```
git clone https://github.com/your-username/offline-ai-chatbot.git
cd offline-ai-chatbot
```

### 2️⃣ Run with Docker
```
docker build -t offline-ai-chatbot .
docker run -p 8501:8501 offline-ai-chatbot
```
Once running, open http://localhost:8501 in your browser to start chatting.

### 🖥 Manual Setup (without Docker)
Prerequisites: Python 3.12.9 and Ollama installed.
```
pip install -r requirements.txt
streamlit run app.py
```
---

### 🤝 Contributing
Fork this repository.
Create a new branch: feature/new-feature
Commit your changes.
Submit a pull request.

### 📜 License
This project is licensed under the MIT License.

### 👨‍💻 Author
Zafer Öztürk
📧 Email: zaferozturkdev@gmail.com
🔗 LinkedIn: linkedin.com/in/zaferozturk
