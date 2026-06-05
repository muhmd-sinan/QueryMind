# AskSQL React Frontend

Professional glassmorphism React frontend for AskSQL Text-to-SQL application.

## Quick Start

### 1. Install Python Dependencies

```bash
pip install flask flask-cors
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
cd frontend
npm install
```

### 3. Start Flask Backend

From the root directory:

```bash
python api.py
```

The API will run on **http://localhost:5001**

### 4. Start React Frontend

In a new terminal:

```bash
cd frontend
npm run dev
```

The app will run on **http://localhost:5173**

## Architecture

```
SQL v3/
├── api.py              # Flask REST API (port 5001)
├── app.py              # Existing Groq query logic
├── db.py               # Existing database utilities
├── frontend/           # React + Vite frontend (port 5173)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── hooks/
│   └── package.json
└── ui.py               # Streamlit UI (alternative)
```

## Features

- 🎨 **Glassmorphism Design**: Dark & light mode with frosted glass effects
- 🔌 **Database Connection**: MySQL database management with live schema
- 🤖 **API Configuration**: Groq API key setup with model selection
- 💬 **Query Interface**: Natural language → SQL → results table
- 📋 **Query History**: Modal popup with past queries
- 📊 **Schema Visualization**: Always-visible database schema grid
- 📥 **CSV Export**: One-click export of query results
- 🌗 **Theme Toggle**: Dark/light mode switcher

## API Endpoints

- `POST /api/connect-db` - Connect to MySQL database
- `POST /api/disconnect-db` - Disconnect from database
- `GET /api/get-schema` - Get current schema
- `POST /api/configure-api` - Configure Groq API key
- `POST /api/query` - Execute natural language query
- `GET /api/history` - Get query history
- `POST /api/clear-history` - Clear history
- `GET /api/status` - Get connection status

## Tech Stack

- **Backend**: Flask, Flask-CORS
- **Frontend**: React 19, TypeScript, Vite
- **Styling**: Tailwind CSS 4
- **Icons**: Lucide React
- **Fonts**: Inter, JetBrains Mono

## Development

### Build for Production

```bash
cd frontend
npm run build
```

Built files will be in `frontend/dist/`

### Run Linter

```bash
cd frontend
npm run lint
```

### Preview Production Build

```bash
cd frontend
npm run preview
```

## Screenshots

### Database Connect Page
- MySQL connection form
- Live schema visualization
- Connection status indicators

### API Configuration Page
- Groq API key input
- Model selection
- Verification status

### Query Interface
- Natural language input
- SQL code display
- Results table with CSV export
- Schema overview grid

## Notes

- The existing `app.py`, `db.py`, and `ui.py` are **unchanged**
- Flask runs on port **5001** to avoid conflicts
- React dev server runs on port **5173**
- Session state is managed in-memory on Flask backend
- For production, add proper session/database storage

## License

Open-source for educational and development purposes.
