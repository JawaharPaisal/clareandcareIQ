# Clare & CareIQ 🏥🤖

**AI-Powered Multimodal Healthcare Assistant for Medical Document Understanding**

Clare & CareIQ is a full-stack AI healthcare assistant designed to help users interact with medical information through **document analysis, medical question answering, OCR, and multimodal AI**.

The system combines **Gemini AI, medical language models, vision-language models, and Biomedical Named Entity Recognition** into a hybrid AI pipeline for processing medical reports and images.

> **Core idea:** Transform unstructured medical documents and images into structured, understandable information using a combination of specialized AI models rather than relying on a single model.

---

## 🧠 AI Architecture

Clare & CareIQ uses a **hybrid multi-model architecture** where different AI components handle different aspects of medical information processing.

```text
                 Medical Report
                /              \
               /                \
        PDF / Text              Image
             │                    │
             ▼                    ▼
      Document Processing        OCR
             │                    │
             └─────────┬──────────┘
                       ▼
              Medical Information
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Gemini       MedAlpaca    Qwen2-VL
          │            │            │
          │         LLaVA-Med       │
          └────────────┼────────────┘
                       ▼
             Biomedical NER
                       │
                       ▼
             Structured Insights
                       │
                       ▼
              Healthcare Assistant
```

The architecture supports **model specialization and fallback workflows**, allowing the application to use different models for different types of medical inputs and processing requirements.

---

## 🤖 AI / ML Components

### 1. Generative AI

**Gemini AI** is integrated into the application for generative AI-powered healthcare interactions and medical information processing.

### 2. Medical Language Models

The system incorporates medical-domain models including:

* **MedAlpaca**
* **LLaVA-Med**

These models provide medical-focused language and multimodal capabilities.

### 3. Vision-Language Models

For image-based medical information processing, the application supports:

* **Qwen2-VL**
* **LLaVA-Med**

This enables the system to work with visual medical information rather than relying exclusively on plain text.

### 4. Biomedical Named Entity Recognition

A **Biomedical NER** pipeline is used to identify relevant medical entities from extracted report information.

Examples of information that can be represented as entities include:

```text
Medical condition
Medication
Symptom
Test / Investigation
Body part
Clinical terminology
```

### 5. OCR & Document Understanding

Medical reports can contain both machine-readable text and image-based information.

The processing pipeline therefore combines:

```text
PDF / Image
     ↓
OCR / Text Extraction
     ↓
Medical Content Processing
     ↓
Entity Extraction
     ↓
AI Interpretation
```

---

## 🔄 Multi-Model Fallback Architecture

One of the key design decisions in Clare & CareIQ is the use of a **multi-model fallback strategy**.

Instead of depending entirely on one AI model:

```text
                  User Input
                      │
                      ▼
              Input Classification
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
      Text Input              Image Input
          │                       │
          ▼                       ▼
      AI Model              Vision Model
          │                       │
          └───────────┬───────────┘
                      ▼
               Result Validation
                      │
                 Failure?
                 /      \
               Yes       No
                │         │
                ▼         ▼
          Fallback Model  Result
                │
                ▼
             Result
```

This architecture is intended to improve reliability when a particular model is unavailable, unsuitable for an input type, or unable to produce the expected result.

---

## ✨ Key Features

### 📄 Medical Report Analysis

Upload medical reports and process their contents using document processing, OCR, NLP and generative AI.

### 🖼️ Medical Image Understanding

Process image-based medical information using multimodal vision-language models.

### 💬 AI Healthcare Assistant

Interact with the application through an AI-powered conversational interface for healthcare-related information.

### 🧬 Biomedical Entity Extraction

Extract medically relevant entities from processed content using Biomedical NER.

### 🔀 Hybrid AI Pipeline

Combines multiple AI approaches instead of depending on a single model:

* Generative AI
* Medical LLMs
* Vision-language models
* NLP
* OCR
* Named Entity Recognition

### 🔐 Privacy & Security

The application includes security mechanisms such as:

* JWT authentication
* Encrypted record storage
* Rate limiting
* Consent handling
* Secure backend APIs

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│              React + Vite UI                │
│                                             │
│  Dashboard │ AI Chat │ Reports │ Profile   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│              Flask Backend                  │
│                                             │
│ Authentication │ Reports │ Chat │ History  │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌─────────────────────────┐
│   MongoDB    │  │      AI Pipeline        │
│              │  │                         │
│ Users        │  │ Gemini                  │
│ Sessions     │  │ MedAlpaca               │
│ Reports      │  │ Qwen2-VL                │
│ Medical Data │  │ LLaVA-Med              │
└──────────────┘  │ Biomedical NER          │
                  │ OCR / Document Analysis │
                  └─────────────────────────┘
```

---

## 🛠️ Technology Stack

| Layer               | Technologies                                |
| ------------------- | ------------------------------------------- |
| Frontend            | React, Vite, Tailwind CSS                   |
| Backend             | Python, Flask                               |
| Database            | MongoDB                                     |
| Generative AI       | Gemini AI                                   |
| Medical LLMs        | MedAlpaca, LLaVA-Med                        |
| Vision-Language AI  | Qwen2-VL, LLaVA-Med                         |
| NLP                 | Biomedical NER                              |
| Document Processing | PDF / OCR                                   |
| Authentication      | JWT                                         |
| Security            | Rate Limiting, Encryption, Consent Handling |

---

## 📁 Repository Structure

```text
Clare-CareIQ/
│
├── frontend/                  # React + Vite application
│
├── server/                    # Flask backend
│   ├── app.py
│   ├── API blueprints
│   ├── middleware
│   └── AI / model integration
│
├── server/requirements.txt    # Python dependencies
├── frontend/package.json      # Frontend dependencies
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

* Node.js 16+
* npm
* Python 3.11+
* MongoDB
* Docker (optional)

### 1. Clone the repository

```bash
git clone https://github.com/JawaharPaisal/Clare-CareIQ.git
cd Clare-CareIQ
```

### 2. Configure the Backend

```bash
cd server

python -m venv venv
```

Activate the environment.

**Windows:**

```powershell
.\venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
copy env.example .env
```

Configure the required environment variables.

### 3. Start MongoDB

Using Docker:

```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

Or use an existing MongoDB instance.

### 4. Start the Flask Backend

```bash
python app.py
```

Backend:

```text
http://localhost:5000
```

### 5. Start the Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on the Vite development port configured by the project.

---

## 🔒 Security & Privacy

Healthcare applications require careful handling of user information.

Clare & CareIQ incorporates:

* JWT-based authentication
* Encrypted record storage
* Consent handling
* Rate limiting
* Protected backend APIs

> **Disclaimer:** Clare & CareIQ is an experimental software project for AI-assisted healthcare information processing. It is not intended to replace qualified medical professionals, diagnosis, or clinical decision-making.

---

## 📸 Screenshots

### Healthcare Dashboard

<img width="1917" height="1021" alt="Clare & CareIQ dashboard" src="https://github.com/user-attachments/assets/d1953dd5-aef0-4c90-8ce9-03deb87ab159" />

### AI Healthcare Assistant

<img width="996" height="700" alt="Clare & CareIQ AI assistant" src="https://github.com/user-attachments/assets/9d3f0515-fccd-4e90-a177-e84d19b51c0e" />

### Medical Report Processing

<img width="1919" height="1059" alt="Clare & CareIQ medical report processing" src="https://github.com/user-attachments/assets/16a66ed1-807f-4a54-a472-2c5e38f41ed0" />

### Healthcare Analytics

<img width="1195" height="908" alt="Clare & CareIQ analytics" src="https://github.com/user-attachments/assets/d7c05314-7a9f-42fd-a4f9-c26478784dee" />

---

## 🔮 Future Directions

Potential directions for extending the project include:

* Improved medical document extraction
* More robust multimodal model routing
* Additional medical-domain models
* Evaluation benchmarks for model responses
* Improved model selection and fallback policies
* Retrieval-augmented generation for medical knowledge
* More comprehensive evaluation of AI-generated insights

---

## 👨‍💻 Project

**Clare & CareIQ**

A full-stack experiment in combining **Generative AI, multimodal AI, medical NLP, computer vision, and secure application engineering** for healthcare information processing.

Built with **Python + Flask + React + MongoDB + Gemini + Medical AI Models**.
