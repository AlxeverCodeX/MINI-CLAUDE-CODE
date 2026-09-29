# Mini Claude Code

A minimal, terminal-based coding agent powered by `claude-opus-4.8`. It gives an LLM the ability to list, read, write files and run shell commands in your working directory via OpenAI-compatible tool calling — inspired by Claude Code.

> Built with Python, the OpenAI SDK, and a simple REPL loop.

---

## Features

- **Interactive REPL** - Chat with the agent directly in your terminal
- **File System Tools** - List directories, read and write files autonomously
- **Shell Execution** - Run shell commands with explicit user approval (`y/n` prompt)
- **Tool-Calling Loop** - Autonomous multi-step execution until the task is complete
- **OpenAI-Compatible API** - Works with any OpenAI-compatible endpoint (default: [cleanapis.com](https://cleanapis.com/?ref=CCUXSZQ9))

## How It Works

1.  You type a task in the terminal (e.g., "create a python script that sorts files")
2.  `agent.py` sends your message + system prompt + tool schemas to `claude-opus-4.8`
3.  The model decides to call tools (`list_files`, `read_file`, `write_file`, `run_command`)
4.  `run_tool()` executes the requested Python function locally and returns the result to the model
5.  Loop repeats until the model responds with plain text (no more tool calls)
6.  The final answer is printed as `Agent: ...`

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_files` | List files/folders in a directory. Folders end with `/` | `path` (string, default `"."`) |
| `read_file` | Read a text file as UTF-8 | `path` (string) |
| `write_file` | Create or overwrite a text file | `path` (string), `content` (string) |
| `run_command` | Run a shell command (requires user confirmation) | `command` (string) |

## Project Structure

```
.
├── agent.py         # Main agent loop + tool definitions
├── pyproject.toml   # Project metadata and dependencies
├── uv.lock          # Locked dependencies (uv)
├── .python-version  # Python version pin
├── .env.example     # Template for required environment variables
└── README.md        # This file
```

## Requirements

- Python >= 3.11
- Dependencies: `openai>=3.19.2`, `python-dotenv>=1.0.0` (see `pyproject.toml`)

## Getting a Free API Key

This agent uses an OpenAI-compatible API, so you can use **any** provider. The default is [CleanAPIs](https://cleanapis.com/?ref=CCUXSZQ9) which provides free credits for `claude-opus-4.8`.

### Option A: CleanAPIs (Recommended - Free Credits)

1. Go to **[https://cleanapis.com/?ref=CCUXSZQ9](https://cleanapis.com/?ref=CCUXSZQ9)** and create an account
2. Navigate to **Dashboard > API Keys**
3. Click **Create New Key** and copy it (starts with `cc_...`)
4. Use it in the Configuration step below

> New accounts get free credits — enough to run this agent for hundreds of requests without a credit card.

### Option B: Any OpenAI-Compatible Provider

You can also swap the endpoint with zero code changes — just change the env vars:

| Provider | `CLEANAPIS_BASE_URL` | `MODEL` example | Free Tier |
|----------|----------------------|-----------------|-----------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` | $5 free credit for new accounts |
| **OpenRouter** | `https://openrouter.ai/api/v1` | `anthropic/claude-3.5-sonnet` | Free models available |
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.1-70b-versatile` | Generous free tier |
| **Ollama (Local)** | `http://localhost:11434/v1` | `llama3.1` | 100% free & offline |

Just set `CLEANAPIS_BASE_URL` and `MODEL` to match your provider — the agent loop stays the same.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AlxeverCodeX/MINI-CLAUDE-CODE.git
cd MINI-CLAUDE-CODE
```

### 2. Create a virtual environment

Using `uv` (recommended):

```bash
uv sync
```

Or using `pip`:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
pip install python-dotenv  # optional, for .env support
```

Or directly:

```bash
pip install "openai>=3.19.2" python-dotenv
```

## Configuration

`agent.py` loads credentials from environment variables — no keys are hardcoded.

It reads:

```python
client = OpenAI(
    api_key=os.getenv("CLEANAPIS_API_KEY"),
    base_url=os.getenv("CLEANAPIS_BASE_URL", "https://cleanapis.com/v1"),
)
MODEL = os.getenv("MODEL", "claude-opus-4.8")
```

### Option A: `.env` file (recommended for local dev)

```bash
cp .env.example .env
# then edit .env with your real key
```

`.env` example:

```
CLEANAPIS_API_KEY=your-api-key-here
CLEANAPIS_BASE_URL=https://cleanapis.com/v1
MODEL=claude-opus-4.8
```

> `.env` is gitignored — it will never be pushed to GitHub. Requires `pip install python-dotenv` (otherwise set vars via Option B).

### Option B: Environment variables

```bash
export CLEANAPIS_API_KEY="your-api-key-here"
export CLEANAPIS_BASE_URL="https://cleanapis.com/v1"
export MODEL="claude-opus-4.8"
```

If `CLEANAPIS_API_KEY` is not set, the agent will print a warning on startup and API calls will fail.

## Usage

Run the agent:

```bash
python agent.py
```

You will see:

```
Mini agent ready.Type 'exit' to quit.

You:
```

### Example Session

```
You: list the files in this directory and create a hello.py that prints hello world

 tool: list_files ({'path': '.'})
 tool: write_file ({'path': 'hello.py', 'content': 'print("hello world")'})

Agent: Created hello.py and verified the directory contents. You can run it with `python hello.py`.

You: exit
```

Type `exit` or `quit` to leave.

## Security Notes

- `run_command` will **always ask for confirmation** (`Run '...' ? [y/n]`) before executing. Never auto-approve untrusted commands.
- The agent runs with the same file-system permissions as the user who launched it. It can read/write any file you can.
- Do not commit real API keys to GitHub. Use `.env` + `.gitignore` or environment variables.
- `subprocess.run(..., shell=True)` is used — be cautious with untrusted model output.
- **If your key was previously committed:** rotate/revoke it immediately at your provider's dashboard and clean git history (e.g., `git filter-repo` or BFG) — adding to `.gitignore` alone does not remove it from history.

## Customization

- **Change the System Prompt:** Edit `SYSTEM_PROMPT` at the top of `agent.py` to change the agent's behavior and personality.
- **Add Tools:** Define a new Python function, add it to the `TOOLS` dict, and add its JSON schema to `TOOL_SCHEMAS`.
- **Switch Models/Providers:** Change `MODEL` and `base_url` to use any OpenAI-compatible provider (OpenAI, Anthropic via proxy, local Ollama, etc.).

Example adding a new tool:

```python
def count_lines(path):
    with open(path) as f:
        return str(len(f.readlines()))

# then add to TOOLS and TOOL_SCHEMAS
```

## Troubleshooting

- **Authentication Error:** Check your `api_key` and `base_url`. Verify the key at your provider's dashboard.
- **Model not found:** Ensure `MODEL` matches a model available on your endpoint.
- **No output on command:** The agent returns `(no output, exit code N)` when stdout/stderr is empty.

## License

MIT — feel free to fork, modify and use for your own projects.

## Contributing

Pull requests are welcome! Please open an issue first to discuss major changes.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-tool`)
3. Commit your changes
4. Push and open a PR

---

**From-scratch reimplementation of Claude Code's core agentic loop — autonomous tool orchestration, recursive function-calling, and human-in-the-loop shell execution distilled into <150 lines of Python. Built to be read in 5 minutes, forked in 10, and extended into production-grade AI agents. If you understand this loop, you can build your own Claude Code.**
