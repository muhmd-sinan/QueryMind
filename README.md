# AskSQL

Natural Language SQL Query Generator with modern glassmorphism web interface.

Convert natural language questions into SQL queries using Groq LLMs and execute them directly on a MySQL database through an interactive web interface.

---

## Features

- **Natural Language → SQL** - Ask questions in plain English
- **Groq LLM Integration** - Fast inference with Groq API
- **MySQL Support** - Connect to any MySQL database
- **Modern UI** - React + Flask with glassmorphism design
- **Schema Visualization** - Live database schema display
- **Query History** - Track and revisit past queries
- **CSV Export** - Export query results
- **Dark Mode** - Professional dark theme
- **No Hardcoded Secrets** - All credentials entered at runtime

---

## Project Structure

```
AskSQL/
├── api.py                    # Flask REST API backend
├── app.py                    # Groq LLM query generation
├── db.py                     # Database utilities
├── ui.py                     # Streamlit UI (alternative)
├── start.bat                 # Windows startup script
├── requirements.txt          # Python dependencies
├── frontend/                 # React web application
│   ├── package.json          # Node dependencies
│   ├── vite.config.js       # Vite configuration
│   ├── tailwind.config.js   # Tailwind CSS config
│   ├── postcss.config.js    # PostCSS config
│   ├── index.html           # Entry HTML
│   └── src/
│       ├── App.tsx          # Main application
│       ├── index.css        # Global styles
│       ├── components/      # UI components
│       │   ├── GlassCard.tsx
│       │   ├── Layout.tsx
│       │   ├── SchemaGrid.tsx
│       │   ├── QueryInput.tsx
│       │   ├── ResultsTable.tsx
│       │   └── HistoryModal.tsx
│       ├── pages/           # Application pages
│       │   ├── DatabaseConnect.tsx
│       │   ├── APIConfig.tsx
│       │   └── QueryInterface.tsx
│       ├── services/        # API client
│       │   └── api.ts
│       └── utils/           # Utilities
│           └── export.ts
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, Flask-CORS |
| Database | MySQL |
| LLM | Groq API |
| Frontend | React 19, TypeScript |
| Build | Vite |
| Styling | Tailwind CSS 4 |
| Icons | Lucide React |
| Fonts | Inter, JetBrains Mono |

---

## Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- MySQL database
- Groq API key (free at [console.groq.com](https://console.groq.com))

### Setup

1. **Clone the repository**
   ```bash
git clone https://github.com/<username>/asksql.git
cd asksql
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

---

## Running the Application

### Option 1: Using start.bat (Windows)

```bash
start.bat
```

This opens two terminal windows:
- Flask backend on port 5001
- React frontend on port 5173

### Option 2: Manual Start

**Terminal 1 - Flask Backend:**
```bash
python api.py
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
```

### Access the Application

Open **http://localhost:5173** in your browser.

### Alternative: Streamlit UI

```bash
streamlit run ui.py
```

---

## Usage

1. **Database Connect** - Enter your MySQL credentials
2. **API Configuration** - Add your Groq API key
3. **Query Interface** - Type natural language questions

### Example Queries

```
Show all employees in Engineering department.

List the top 10 highest paid employees.

How many orders were placed this month?

Show total revenue by product category.

Find customers who haven't placed orders in 6 months.
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/connect-db` | Connect to MySQL |
| POST | `/api/disconnect-db` | Disconnect from database |
| GET | `/api/get-schema` | Get database schema |
| POST | `/api/configure-api` | Configure Groq API |
| POST | `/api/clear-api` | Clear API configuration |
| POST | `/api/query` | Execute natural language query |
| GET | `/api/history` | Get query history |
| POST | `/api/clear-history` | Clear history |
| GET | `/api/status` | Get connection status |

---

## Architecture

```
┌─────────────────┐     HTTP      ┌─────────────────┐
│   React Frontend │◄────────────►│   Flask Backend │
│   (Port 5173)    │              │   (Port 5001)    │
└─────────────────┘              └────────┬────────┘
                                          │
                           ┌──────────────┴──────────────┐
                           ▼                             ▼
                  ┌─────────────────┐          ┌─────────────────┐
                  │   Groq LLM API  │          │   MySQL Database │
                  │   (Query Gen)   │          │   (Data Store)   │
                  └─────────────────┘          └─────────────────┘
```

---

## Configuration

### Default Values (Pre-filled in UI)

| Setting | Default |
|---------|---------|
| Host | `localhost` |
| Port | `3306` |
| User | `root` |
| Database | `company_db` |
| Model | `openai/gpt-oss-120b` |

### Environment Variables

Create `.env` file (optional):
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=your_database
GROQ_API_KEY=your_api_key
```

---

## Security

- All credentials entered at runtime (not stored)
- API keys sent only to Groq API
- Database passwords never logged
- Session-scoped state (cleared on restart)

---

## Development

### Build for Production

```bash
cd frontend
npm run build
```

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

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 5001
netstat -ano | findstr :5001

# Kill process (replace PID)
taskkill /PID <pid> /F
```

### Module Not Found

```bash
pip install flask flask-cors mysql-connector-python groq pandas
```

### npm Install Fails

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rmdir /s /q node_modules
del package-lock.json
npm install
```

---

## Future Enhancements

- [ ] PostgreSQL support
- [ ] SQL Server support
- [ ] SQLite support
- [ ] Docker deployment
- [ ] User authentication
- [ ] Query explanation mode
- [ ] Multi-database management
- [ ] Query favorites/bookmarks
- [ ] Query templates
- [ ] Result visualization (charts)

---

## License

This project is open-source and available for educational and development purposes.

---

## Credits

- [Groq](https://groq.com) - Fast LLM inference
- [React](https://react.dev) - UI framework
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS
- [Lucide](https://lucide.dev) - Beautiful icons
