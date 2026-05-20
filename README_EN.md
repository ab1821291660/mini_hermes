# Mini-Hermes
A minimal AI agent built from scratch with tool calling, persistent memory, self-improving skills, and context compression. Runs entirely on local models via [LM Studio](https://lmstudio.ai/). Inspired by [Hermes Agent](https://github.com/nousresearch/hermes-agent). For educational purposes only.
**Blog post:** [Build a Mini Hermes Agent From Scratch](https://mesuvash.github.io/projects/mini-hermes/)
**Blog post:**https://mesuvash.github.io/projects/mini-hermes/

## What it does
Mini-Hermes is a terminal-based AI assistant that goes beyond simple chat. It can execute shell commands, read/write files, remember things across sessions, learn reusable skills from experience, and manage its own context window when conversations get long.
```
╔══════════════════════════════════════╗
║       Mini-Hermes Agent v0.1         ║
║  /mem /skills /model /sessions       ║
║  exit to quit                        ║
╚══════════════════════════════════════╝
  Model: qwen3.5-35b-a3b
  Session: a1b2c3d4...
  Memory: loaded | Skills: 2

you > what files are in this directory?
hermes > [runs terminal tool, returns results]
```
## Architecture
```
cli.py                  # REPL interface, wires everything together
├── agent.py            # Core agent loop (message → tools → response)
├── tool_calling.py     # Strategy pattern for structured vs text-based tool calling
├── tool_registry.py    # Global tool registry with OpenAI-compatible schemas
├── prompt_builder.py   # Assembles frozen system prompt per session
├── prompt_caching.py   # Anthropic-style cache breakpoints (system_and_3)
├── compression.py      # Middle-out context compression with memory flush
├── tools/
│   ├── terminal.py     # Shell command execution
│   ├── file_tools.py   # Read/write files
│   └── memory_tool.py  # Save observations, search past sessions
├── memory/
│   ├── persistent.py   # MEMORY.md + USER.md on disk
│   ├── session_db.py   # SQLite + FTS5 episodic memory
│   └── recall.py       # Cross-session search with LLM summarization
└── skills/
    ├── loader.py       # Discover and parse SKILL.md files
    └── manager.py      # Create, patch, delete skills at runtime
```
## Key concepts
**Dual tool-calling strategies.** Models with native function calling (Qwen, Mistral, Hermes) use the OpenAI `tools` API parameter. Models without it (Gemma, LLaMA) get tool schemas injected into the system prompt and tool calls are parsed from text output via regex. The agent picks the right strategy automatically based on model name.

**Three-tier memory.** (1) Persistent memory in flat markdown files (`MEMORY.md`, `USER.md`) loaded as a frozen snapshot into the system prompt at session start. (2) Episodic memory in SQLite with FTS5 full-text search across all past sessions. (3) Cross-session recall that searches FTS5, groups by session, and summarizes relevant history via an LLM call.

**Self-improving skills.** The agent can create, edit, and delete `SKILL.md` files -- reusable procedures it discovers during conversations. Skills use YAML frontmatter for metadata and are progressively disclosed: the system prompt only gets a one-line index, and the agent loads full skill content on demand.

**Learning loop.** Nudge counters track turns since the agent last used memory or skills. When thresholds are crossed, a background review agent spawns on a separate thread to scan the conversation for observations worth saving or skills worth creating -- without blocking the main conversation.

**Context compression.** When the conversation approaches the context window limit, a middle-out compression fires: the system prompt (head) and recent messages (tail) are preserved, and the middle section is summarized by the LLM. Before compression, a memory flush gives the agent one turn to save important observations.

**Prompt caching (Anthropic).** Optional `cache_control` breakpoints on the system prompt plus the last three non-system messages (`system_and_3`). Wired in `agent_loop._call_llm` and controlled from `config.yaml`. With DeepSeek or LM Studio, leave `prompt_caching.enabled: false` (default); the provider gate skips injection on non-Anthropic `base_url` values even if enabled. To use it for real cost/latency wins, switch to an Anthropic-compatible endpoint, set `enabled: true` and `provider: anthropic`, then run multi-turn sessions and watch logs for `cache_read_input_tokens` on later turns.


## Setup
Requires Python 3.10+ and a local model server (LM Studio, Ollama with OpenAI-compatible endpoint, etc.).
```bash
./setup.sh
```
Or manually:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Configuration
Edit `config.yaml` to point at your model server:
```yaml
model:
  api_key: "lm-studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen3.5-35b-a3b"
  max_tokens: 400
```
Any OpenAI-compatible API works. Change `base_url` and `model` to match your setup.

Optional Anthropic prompt caching (off by default):

```yaml
prompt_caching:
  enabled: false
  provider: auto    # auto | anthropic | off
  cache_ttl: 5m     # 5m | 1h
  log_usage: true
```

When moving to Claude, point `model.base_url` at Anthropic (or a compatible proxy), set `prompt_caching.enabled: true` and `provider: anthropic`, then verify cache hits in the CLI log after the second turn.

## Usage
```bash
source .venv/bin/activate
python cli.py ##===================================
```

### Slash commands

| Command | Description |
|---------|-------------|
| `/mem` | Show current memory and user profile |
| `/skills` | List learned skills |
| `/model` | Switch between available models (interactive picker) |
| `/sessions` | Search past sessions by keyword |
| `exit` | Quit |

### Built-in tools

The agent has access to these tools and uses them autonomously:

| Tool | What it does |
|------|-------------|
| `terminal` | Execute shell commands |
| `read_file` | Read file contents |
| `write_file` | Write/create files |
| `memory` | Save observations, update user profile, search past sessions |
| `skills_list` | List available skills |
| `skill_view` | Load full skill content |
| `skill_manage` | Create, patch, or delete skills |

## Data

All runtime data lives in `data/` (gitignored):

- `data/state.db` -- SQLite database with session history and FTS5 index
- `data/MEMORY.md` -- Persistent observations
- `data/USER.md` -- User profile
- `data/skills/` -- Learned skill definitions

## Companion blog post

See [Build a Mini Hermes Agent From Scratch](https://mesuvash.github.io/projects/mini-hermes/) for a detailed walkthrough of the design decisions behind each component.
all：https://github.com/search?q=mini+hermes&type=repositories
参考：https://github.com/mesuvash/mini_hermes
参考：https://github.com/tangfei-china/mini-hermes
参考：https://github.com/JerryZ01/hermes-mini ----

