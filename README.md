# AI Code Reviewer

An intelligent code analysis tool that reviews Python and JavaScript code for bugs, security vulnerabilities, performance issues, and complexity — all powered by AI.

## Features

- **Bug Detection** - AI-powered identification of logic errors and runtime issues
- **Security Analysis** - Detect common security vulnerabilities (SQL injection, XSS, etc.)
- **Optimization Suggestions** - Performance improvements and best practices
- **Complexity Analysis** - Cyclomatic complexity, nesting depth, LOC, and more
- **Refactoring Suggestions** - Code structure improvements
- **Report Generation** - Download detailed HTML review reports
- **File Upload & Paste** - Upload `.py`/`.js` files or paste code directly

## Tech Stack

- **Backend:** Python, FastAPI
- **AI:** OpenAI GPT
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templates)
- **Database:** SQLite

## Project Structure

```
ai-code-reviewer/
├── app.py                         # FastAPI main application
├── models.py                      # Pydantic data models
├── database.py                    # SQLite database setup
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore
├── services/
│   ├── review_service.py          # Review orchestration
│   ├── bug_detector.py            # AI + rule-based bug detection
│   ├── security_checker.py        # AI + rule-based security analysis
│   ├── optimization_service.py    # Performance optimization suggestions
│   ├── complexity_analyzer.py     # Cyclomatic complexity calculation
│   └── report_service.py          # HTML report generation
└── templates/
    ├── index.html                 # Frontend interface
    └── report.html                # Downloadable report template
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-code-reviewer.git
cd ai-code-reviewer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up environment variables (optional)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Without an API key, the reviewer still provides rule-based analysis including:
- Cyclomatic complexity scoring
- Security pattern detection
- Basic bug detection
- Code metrics

### 4. Run the application

```bash
python app.py
```

### 5. Open in browser

Navigate to: `http://localhost:8000`

## Project Flow

1. **Paste or Upload Code** → Write code in the editor or upload a `.py`/`.js` file
2. **Select Language** → Choose Python or JavaScript
3. **Review** → Click the review button to analyze
4. **View Results** → Results are shown in tabs:
   - **Bugs** - Detected bugs with line numbers and severity
   - **Security** - Security vulnerabilities and risk levels
   - **Optimization** - Performance tips and best practices
   - **Complexity** - Metrics grid (cyclomatic complexity, LOC, nesting depth, etc.)
   - **Refactoring** - Code structure improvement suggestions
5. **Download Report** → Generate and download a detailed HTML report

## Complexity Metrics

| Metric | Description |
|--------|-------------|
| Cyclomatic Complexity | Number of independent paths through the code |
| Lines of Code | Total lines excluding blanks and comments |
| Function Count | Number of defined functions |
| Class Count | Number of defined classes |
| Max Nesting Depth | Deepest nesting level of control structures |
| Avg Function Complexity | Average complexity per function |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Frontend interface |
| POST | `/api/review` | Submit code for review |
| GET | `/api/review/{id}` | Get review results |
| POST | `/api/review/{id}/report` | Download HTML report |
