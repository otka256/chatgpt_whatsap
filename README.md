<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/OpenAI-ChatGPT-412991?style=for-the-badge&logo=openai" alt="OpenAI" />
  <img src="https://img.shields.io/badge/WhatsApp-Automation-25D366?style=for-the-badge&logo=whatsapp" alt="WhatsApp" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License" />
</p>

<h1 align="center">🤖 WhatsApp ChatGPT AI Assistant</h1>

<p align="center">
  <b>A lightweight, automated Python bridge connecting OpenAI ChatGPT with WhatsApp messaging for autonomous responses and ambient data ingestion.</b>
</p>

---

## ⚡ Features
- 💬 **Intelligent Auto-Replies**: Bridges WhatsApp incoming queries with OpenAI models in real time.
- 🌐 **Environmental Data Fetching**: Retrieves system & ambient metrics alongside chat completions.
- 🚀 **Asynchronous & Lightweight**: Built for reliable continuous execution with minimal overhead.

## 🛠️ Setup & Usage

### 1. Requirements
```bash
pip install openai requests python-dotenv
```

### 2. Environment Variables
Set your API credentials in your environment or a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
MESSAGE_WALL_API=your_gateway_api_key_here
```

### 3. Run
```bash
python auto_whatsap.py
```

---
*Developed with focus on automation & AI integration by [otka256](https://github.com/otka256).*
