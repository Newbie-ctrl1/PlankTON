# Copilot Instructions

This is a Flask web application for plant analysis and agricultural AI chatbot.

## Project Overview

Plankton is an AI-powered agricultural assistant that combines:
- Plant identification via Plant.id API
- Groq AI chatbot for plant-focused discussions
- Chat history storage with SQLite
- Responsive web interface

## Key Technologies

- **Backend**: Flask, Flask-SQLAlchemy, Python 3.8+
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: Plant.id (plant identification), Groq (AI)
- **Database**: SQLite
- **Environment**: Python virtual environment with pip

## Project Structure

```
plankton/
├── app/
│   ├── __init__.py (Flask factory)
│   ├── models.py (Database models)
│   ├── routes/ (API endpoints)
│   ├── services/ (External API integration)
│   ├── templates/ (HTML templates)
│   └── static/ (CSS, JS, uploads)
├── run.py (Entry point)
└── requirements.txt (Dependencies)
```

## Setup Steps

1. **Create virtual environment**: `python3 -m venv venv`
2. **Activate venv**: `source venv/bin/activate`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Configure environment**: Copy `.env.example` to `.env` and add API keys
5. **Run application**: `python run.py`

## API Keys Required

- **Plant.id API Key**: https://plant.id
- **Groq API Key**: https://console.groq.com

## Common Commands

```bash
# Run development server
python run.py

# Install packages
pip install -r requirements.txt

# Reset database
rm app/plankton.db
python run.py
```

## API Endpoints

- `POST /api/chat/send` - Send chat message
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history/<id>` - Delete chat
- `POST /api/plant/analyze` - Analyze plant from image
- `GET /api/plant/history` - Get analysis history

## Troubleshooting

- **Import errors**: Verify venv is activated and requirements installed
- **API errors**: Check API keys in `.env`
- **Database errors**: Delete `.db` file to reset
- **Upload errors**: Verify `app/static/uploads` folder exists with write permissions
