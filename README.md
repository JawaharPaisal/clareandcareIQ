# Clare & CareIQ

AI-powered healthcare assistant for medical report analysis, personalized health guidance, and patient support.

## Overview

This repository contains a full-stack healthcare application with:
- React + Vite frontend for interactive health dashboards, AI chat, report upload, and profile management
- Flask backend API for authentication, chat, medical history, reports, and AI integrations
- MongoDB data storage for users, sessions, reports, and medical history
- Local and cloud AI model support for medical NLP and question answering

## Key Features

- Authentication and session management
- Healthcare chatbot assistant
- Medical report upload and analysis
- Patient profile and health analytics
- Secure backend API with JWT, rate limiting, and consent handling
- Local LLM support for offline AI inference

## Repository Structure

- `frontend/` — React app, Vite configuration, Tailwind styling
- `server/` — Flask backend, API blueprints, local model directories, middleware
- `server/requirements.txt` — Python dependencies for backend and AI support
- `frontend/package.json` — frontend dependencies and npm scripts

## Prerequisites

- Node.js 16+ and npm
- Python 3.11+ (compatible with backend dependencies)
- MongoDB instance or Docker container

## Setup

### Backend

1. Change to the server folder:
   ```bash
   cd server
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create environment variables from example:
   ```bash
   copy env.example .env
   ```
5. Start MongoDB locally or with Docker:
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```
6. Run the Flask API:
   ```bash
   python app.py
   ```

### Frontend

1. Change to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install frontend dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open the app in your browser at `http://localhost:3000`

## Important Notes

- The repository includes large local model directories, such as `server/llava-med-v1.5-mistral-7b/` and `server/Qwen2-VL-7B-Instruct/`.
- A root `.gitignore` file has been added to exclude:
  - `node_modules/`
  - `**/llms/**` and local model weight folders
  - `*.txt` and `*.md`
  - Python cache files and common editor directories

## Running the App

- Frontend: `cd frontend && npm run dev`
- Backend: `cd server && python app.py`
- The backend defaults to `http://localhost:5000`
- The frontend defaults to `http://localhost:3000` or the Vite port assigned by config

## Deployment

For production deployment, build the frontend and serve it using a static host or integrate it with the Flask backend.

### Frontend production build

```bash
cd frontend
npm run build
``` 

### Backend production

- Use a production WSGI server such as Gunicorn or uWSGI
- Configure environment variables securely
- Secure MongoDB access and enable HTTPS in the production environment

## Useful Commands

### Frontend
- `npm install`
- `npm run dev`
- `npm run build`
- `npm run preview`

### Backend
- `pip install -r requirements.txt`
- `python app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

## Screenshots
<img width="1917" height="1021" alt="Screenshot 2025-09-11 131559" src="https://github.com/user-attachments/assets/d1953dd5-aef0-4c90-8ce9-03deb87ab159" />

<img width="996" height="700" alt="Screenshot 2025-09-11 133119" src="https://github.com/user-attachments/assets/9d3f0515-fccd-4e34-a177-e84d19b51c0e" />

<img width="1919" height="1059" alt="Screenshot 2025-09-11 134154" src="https://github.com/user-attachments/assets/16a66ed1-807f-4a54-a472-2c5e38f41ed0" />

<img width="1195" height="908" alt="Screenshot 2025-10-29 120204" src="https://github.com/user-attachments/assets/d7c05314-7a9f-42fd-a4f9-c26478784dee" />

Thanking You ...
