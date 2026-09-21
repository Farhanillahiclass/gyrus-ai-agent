# GYRUS

> **A local-first AI desktop assistant for voice interaction, PC automation, research, productivity, and persistent personal memory.**

GYRUS is a Python-based personal AI assistant with a browser-based command dashboard. It brings AI interaction and practical desktop workflows into one unified system, with **local-first execution** as the default.

Built by **Muhammad Farhan**.

---

## ✨ Overview

GYRUS is designed to go beyond a traditional chatbot.

It can understand commands in **Urdu or English**, route requests to specialized tools, execute supported desktop workflows, manage tasks and reminders, perform research, interact with communication tools, and maintain a small persistent local user profile.

### Core principles

- **Local-first AI:** the conversational engine can run directly on the user's machine.
- **Tool-based routing:** a separately trained intent classifier maps requests to specialized capabilities.
- **Privacy-conscious design:** credentials and local model files are kept outside the public repository.

---

## 🧠 Architecture

```text
User
  │
  ├── Voice / Text
  │
  ▼
Command Interface
  │
  ▼
Intent Classifier
  │
  ├── YouTube
  ├── System Control
  ├── Tasks & Reminders
  ├── Files
  ├── Research
  ├── Communication
  ├── Vision / OCR
  └── Study & Diet
  │
  ▼
AI Brain
  │
  ├── Local LLM
  └── Optional Cloud Provider
  │
  ▼
Result
  │
  └── Dashboard / Voice Response
```

The conversational engine can run locally through `llama-cpp-python`.

```bash
python download_model.py
```

Command routing uses a locally trained **TF-IDF + Logistic Regression** classifier based on:

```text
data/intents_dataset.csv
```

Retraining:

```bash
python train_model.py
```

---

## 🚀 Features

| Capability | Status |
|---|---|
| Voice + text assistant | ✅ |
| Urdu + English interaction | ✅ |
| Local LLM | ✅ |
| Trainable intent classifier | ✅ |
| YouTube search & controls | ✅ |
| System controls | ✅ |
| Application & website launcher | ✅ |
| File search & organization | ✅ |
| File rename & move | ✅ |
| AI-assisted filename suggestions | ✅ |
| Tasks & reminders | ✅ |
| Persistent local memory | ✅ |
| Research pipeline | ✅ |
| Weather / news / web research | ✅ |
| PDF / image / text analysis | ✅ |
| OCR | ✅ |
| Face / motion detection | ✅ |
| Study tracker & AI quizzes | ✅ |
| Diet / macro tools | ✅ |
| WhatsApp workflows | ✅ |
| Email tools | ✅ |
| Screenshot & clipboard utilities | ✅ |
| Window management | ✅ |
| Backup utilities | ✅ |
| Social-post preparation | ⚠️ Confirmation required |
| Silent WhatsApp auto-reply | ⚠️ Not included |
| Emotion / mood detection | ⚠️ Requires an appropriate model |

---

## 🖥️ Dashboard

GYRUS includes a dedicated AI command dashboard rather than a conventional chatbot interface.

### Dashboard sections

- **Home** — AI interaction and command center
- **Tasks** — priorities, completion and reminders
- **System** — CPU, RAM, disk, battery and system controls
- **Study & Diet** — study tracking, goals, quizzes and nutrition tools
- **Communicate** — WhatsApp and email workflows
- **Tools** — files, applications, clipboard, OCR and YouTube utilities
- **Research** — multi-source research and downloadable reports
- **Detect** — webcam motion and face detection
- **Settings** — profile, notes, engine status and configuration

The local backend communicates through:

```text
http://127.0.0.1:8765
```

---

## 🔬 Research Engine

The research pipeline combines:

- Wikipedia
- Semantic Scholar
- General web search

The AI synthesizes the collected material into a structured article saved locally:

```text
data/research/<topic>-<date>.md
```

---

## 📁 Smart File Management

GYRUS supports:

- File and folder search
- File organization
- Rename and move operations
- Content-based rename suggestions
- OCR-assisted image analysis
- Backups
- Clipboard utilities

Rename suggestions are presented for user approval rather than silently changing filenames.

---

## 🎙️ Voice Interaction

The interaction pipeline is:

```text
Speech → Intent → AI Brain → Tool → Result → Voice Response
```

Voice mode:

```bash
python main.py
```

Text mode:

```bash
python main.py --text
```

---

## ▶️ YouTube Controls

Supported workflows include:

- Search
- Play / pause / stop
- Skip / rewind / seek
- Volume and mute
- Fullscreen
- Playback speed
- Captions
- Theater mode

Some browser-based controls require the YouTube tab to be focused.

---

## 📚 Productivity & Study

GYRUS includes:

- Task management
- Priority tracking
- Reminders
- Overdue detection
- Study sessions
- Weekly study goals
- AI-generated quizzes
- Voice-to-text notes
- Word document generation
- Persistent local memory

---

## 📄 Document Analysis

The document analyzer supports:

- PDF files
- Images
- Text files

It can summarize documents and answer questions based on their contents.

---

## 💬 Communication

### WhatsApp

- Message sending
- Bulk-send workflows
- Attachments

### Email

- Read
- Send
- Summarize
- Draft

Communication actions should use explicit confirmation before sending where appropriate.

---

# 🛠️ Tech Stack

### Core
- Python
- FastAPI

### AI / ML
- Local LLM
- `llama-cpp-python`
- Hugging Face provider
- scikit-learn
- TF-IDF
- Logistic Regression

### Dashboard
- HTML
- CSS
- JavaScript
- Canvas-based visual components

### Automation
- psutil
- Playwright
- Desktop automation utilities

### Vision
- OCR
- Webcam processing
- Face / motion detection

### Storage
- JSON
- Markdown
- Local files

---

# 📦 Installation

## 1. Clone

```bash
git clone https://github.com/Farhanillahiclass/gyrus-ai-agent.git
cd gyrus-ai-agent
```

## 2. Virtual environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

## 3. Dependencies

```bash
pip install -r requirements.txt
```

## 4. Environment configuration

Create `.env` from `.env.example` and add only the credentials you actually need.

**Never commit `.env` to Git.**

## 5. Check setup

```bash
python check_setup.py
```

## 6. Download the local model

```bash
python download_model.py
```

Optional:

```bash
python download_model.py --size small
python download_model.py --size large
```

The local model is intentionally excluded from GitHub because of its size.

---

# ▶️ Running GYRUS

### CLI assistant

```bash
python main.py
```

### Text mode

```bash
python main.py --text
```

### Dashboard backend

```bash
python server.py
```

Then open:

```text
dashboard/index.html
```

---

# ⚙️ Optional Components

### Windows microphone

```bash
pip install pipwin
pipwin install pyaudio
```

### Browser automation

```bash
playwright install chromium
```

### OCR

Install Tesseract separately for your operating system.

### Windows `llama-cpp-python`

If installation requires native build tools, install **Desktop development with C++** through Visual Studio Build Tools and retry the package installation.

---

# 🔐 Security & Privacy

GYRUS follows a local-first approach.

- `.env` is excluded from Git.
- API keys and credentials should never be hard-coded.
- Email uses an application password rather than a normal account password.
- Login information is intended to use the operating system's secure credential storage.
- Communication automation uses authorized user sessions or supported APIs.
- No CAPTCHA, MFA, authentication, or platform-security bypassing is included.
- The backend listens on `127.0.0.1`.
- Significant file and communication actions remain user-controlled.

---

# 📂 Project Structure

```text
gyrus-ai-agent/
│
├── dashboard/
│   ├── assets/
│   └── index.html
│
├── data/
│   ├── research/
│   ├── screenshots/
│   ├── intents_dataset.csv
│   └── user_profile.json
│
├── models/
├── modules/
│
├── brain.py
├── cloud_brain.py
├── local_brain.py
├── commands.py
├── main.py
├── server.py
├── voice.py
├── train_model.py
├── download_model.py
├── check_setup.py
│
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

> Local LLM model files are intentionally not committed to GitHub.

---

# 🧪 Development

Run the setup check after changes:

```bash
python check_setup.py
```

Retrain the intent classifier when training data changes:

```bash
python train_model.py
```

Test dashboard and backend together when modifying API routes or UI integrations.

---

# 🗺️ Roadmap

- More capable local models
- Improved intent classification
- Multi-step agent workflows
- Expanded tool registry
- Better voice interaction
- Additional desktop integrations
- More research sources
- Stronger permission management
- Expanded automated testing
- Advanced dashboard analytics
- Optional advanced vision capabilities

---

# 👨‍💻 Author

**Muhammad Farhan**

AI Student • AI/ML Developer • Backend & Automation Enthusiast

- GitHub: https://github.com/Farhanillahiclass
- LinkedIn: https://www.linkedin.com/in/muhammadfarhanmrs

---

# 🤝 Credits

Parts of the project build on or reference earlier work from:

- `taskflow-cli`
- `smart-vision-assistant-pro`
- `student-performance-eda-feature-engineering`

See the relevant source files for attribution details.

---

# 📄 License

MIT License

Copyright © 2026 Muhammad Farhan .

See [`LICENSE`](LICENSE) for the full license text.

---

## ⭐ GYRUS

**A local-first AI command center connecting conversation, automation, productivity, and desktop intelligence in one system.**
