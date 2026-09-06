# Local Terminal AI Agent (Ollama + Home Assistant + Voice)

A fully local AI agent that can run shell commands, read/write files, control
smart home devices (lights, AC, switches) via Home Assistant, and optionally
talk to you by voice — no cloud, no API keys, everything runs on your machine.

## 1. Install Ollama and pull a model
**IMPORTANT — pick a model that fits your RAM.** The Modelfile is set to
`qwen2.5-coder:14b`, but a 14b model needs ~9.4 GB just to load into RAM — it
will NOT run on a machine with only 7.5 GB (you'll get
"model requires more system memory ... than is available"). Use the 7b coder
instead (best coding model that fits):
```bash
ollama pull qwen2.5-coder:7b
```
If your machine has ≥16 GB RAM you can pull the 14b instead:
```bash
ollama pull qwen2.5-coder:14b
```

## 2. Build your agent model
Build on whichever base you pulled. To build on the 7b (recommended for this
machine), point the Modelfile's `FROM` line at it:
```bash
# either edit Modelfile:  FROM qwen2.5-coder:7b
# or build from a copy without touching the original:
sed 's|FROM qwen2.5-coder:14b|FROM qwen2.5-coder:7b|' Modelfile > Modelfile.7b
ollama create my-agent -f Modelfile.7b
```
Then set `MODEL_NAME` in `.env` to match what you built (`my-agent`).

## 3. Set up config
```bash
cp config.example.env .env
```
Edit `.env`:
- `HA_URL` / `HA_TOKEN` — needed for lights/AC control (step 5 below)
- Voice settings — only needed if you want `--voice` mode (step 6 below)

## 4. Install Python dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Connect Home Assistant (for lights/AC/switches)
If you don't already run Home Assistant:
- Easiest: install **Home Assistant OS** on a Raspberry Pi or spare machine,
  or run it in Docker: https://www.home-assistant.io/installation/
- Pair your smart plugs/bulbs/AC (Tuya, Zigbee, IR blaster like Broadlink,
  etc.) inside Home Assistant — it has integrations for almost everything.
- In Home Assistant: **Profile → Security → Long-Lived Access Tokens → Create
  Token**. Paste it into `.env` as `HA_TOKEN`, and set `HA_URL` to your HA
  instance's address (e.g. `http://homeassistant.local:8123`).
- Test it works: ask the agent "list my light entities" — it'll call
  `ha_list_entities` and show you the real entity IDs to use (e.g.
  `light.living_room`, `climate.bedroom_ac`).

If a device isn't "smart" (a plain AC with only a remote), you need either a
smart plug (for anything with a physical power button) or an IR blaster like
Broadlink RM4 (learns your AC remote's codes) paired into Home Assistant.

## 6. Set up voice (optional)
**Listening (speech-to-text)** — handled by `faster-whisper`, already in
requirements.txt, downloads its model automatically on first use. Also needs
ALSA tools for recording:
```bash
sudo apt install alsa-utils   # provides `arecord`
```

**Speaking (text-to-speech)** — uses `piper`, a fast local TTS engine:
```bash
# Download the piper binary for your platform:
# https://github.com/rhasspy/piper/releases
# Download a voice model (.onnx + .onnx.json), e.g. en_US-lessac-medium:
# https://github.com/rhasspy/piper/blob/master/VOICES.md
```
Put the binary path and voice model path into `.env` as `PIPER_BINARY` and
`PIPER_MODEL`. Playback uses `aplay` (also from `alsa-utils`, installed above).

## 7. Set up face recognition + auto-welcome (optional)
Note: `face_recognition` depends on `dlib`, which compiles from source — make
sure you have `cmake` and build tools first:
```bash
sudo apt install cmake build-essential
```

Then enroll your face (one-time):
```bash
python3 enroll_face.py
```
This takes 5 photos from your webcam and saves your face data locally to
`face_data.pkl` — nothing leaves your machine.

Set `ENTRY_LIGHT_ENTITY` in `.env` to the light you want to turn on when
you're recognized (e.g. `light.entryway`).

Run the watcher (leave it running in the background):
```bash
python3 presence.py
```
It checks the camera every couple seconds; when it sees your face, it speaks
`WELCOME_MESSAGE` and turns the light on — no confirmation prompt, since this
is meant to happen automatically. There's a cooldown (`WELCOME_COOLDOWN_SECONDS`,
default 10 min) so it doesn't repeat the welcome every time you walk past.

## 8. Set up always-listening / wake word (optional)
Instead of pressing Enter before every voice command, run:
```bash
python3 agent.py --wake
```
It listens continuously for a wake word (default `hey_jarvis`, from
openWakeWord's pretrained models — say "hey jarvis" the way you'd say "hey
siri"), then records your actual command and responds by voice. Change
`WAKEWORD_MODEL` in `.env` if you'd rather use one of openWakeWord's other
pretrained words (`alexa`, `hey_mycroft`).

## 9. Run it
```bash
python3 agent.py            # text mode
python3 agent.py --voice    # press Enter, then speak, per command
python3 agent.py --wake     # always listening, no key press needed
```

For the full "walk in the door" experience, run `presence.py` and
`agent.py --wake` at the same time (two terminals, or set both up as
background services / systemd units so they start automatically at login).

Try things like:
```
you> what lights do I have?
you> turn on the living room light
you> set the bedroom AC to 24 degrees
you> what's the disk usage on this machine?
```

## How it works
- `Modelfile` — the agent's personality ("talk like a friend") and the exact
  tool-call format it uses.
- `agent.py` — the loop: send messages to Ollama → if the reply is a tool
  call, run it (shell/file/Home Assistant) → feed the result back → repeat
  until it gives a final answer. In `--voice` mode, input comes from your mic
  (via `arecord` + `faster-whisper`) and output is spoken back (via `piper` +
  `aplay`).
- `.env` — your secrets and settings (Home Assistant token, voice config).
  Never commit this file.

## Safety notes
- Shell commands and file writes always require confirmation. **In text mode**
  that's typing "y". **In `--voice` or `--wake` mode**, it's fully hands-free —
  the agent speaks "Run this command? Say yes or no" and listens for your
  answer, so you never have to touch the keyboard.
- If you want zero friction — no confirmation step at all, it just does
  whatever you say immediately — set `SKIP_CONFIRM_IN_VOICE=true` in `.env`.
  This is genuinely risky: it means "open terminal", "delete these files",
  and anything else you say by voice runs instantly with no check. Only turn
  this on once you trust the model's judgment and understand a misheard word
  could trigger the wrong command.
- Home Assistant actions (lights, AC) ask for confirmation by default too
  (same voice-or-type behavior); set `HA_REQUIRE_CONFIRM=false` in `.env`
  once you trust it, for instant "turn on the light" with no prompt at all —
  this one's lower-risk than shell/file access, so it's a more reasonable
  thing to disable early.
- File tools are scoped to the directory you run the script from.
- Consider a dedicated, low-privilege Home Assistant token/user if you're
  worried about the agent affecting more than intended — HA lets you scope
  what a token/user can control.

## Improving speed and "smarts"
- Smaller/quantized models respond faster but reason less well — try a couple
  of sizes (7B vs 14B) and see what your hardware handles comfortably.
- Keep Ollama warm (don't let it unload the model between requests) for snappy
  responses — see Ollama's `OLLAMA_KEEP_ALIVE` env var. Note: on a CPU-only box
  without a GPU, even a 7B model takes ~20s per response, and multi-step
  coding tasks run in ~1–2 min. That's the thermal ceiling of CPU inference.
- If the model is slow to find the right entity_id, you can hardcode a
  name→entity_id map in `agent.py` for your most-used devices instead of
  relying on `ha_list_entities` every time.

## Safety note on face recognition
`presence.py` triggers automatically with no confirmation step (turning on
a light is low-risk). If you ever wire face recognition to something higher
stakes — unlocking a door, disarming an alarm — treat that as a security
system, not a hobby script: add a confirmation step, log every trigger, and
understand that `face_recognition`'s matching isn't forensic-grade (tune
`FACE_TOLERANCE` and test in your actual lighting before relying on it).

## Not yet included (future steps)
- **Camera/vision understanding** ("what's on my desk", general scene
  description) — needs a vision-capable local model (e.g. LLaVA, Qwen2-VL)
  in addition to the text model; face recognition above is narrower (just
  matching, not describing).
- **Auto-start on boot/login** — wrap `presence.py` and `agent.py --wake` as
  systemd user services so you don't have to manually start them each time.

## Memory (remember facts across sessions)
The agent can store and recall facts about you so it doesn't forget between
runs. Just ask it to remember something:

```
you> my name is Sam, and my favorite light is the living room
you> what do you remember about me?
you> set the bedroom AC to 24 and remember that for next time
```

It saves to `memory_store/facts.json` (set `MEMORY_PATH` in `.env`). Nothing
leaves your machine. The `remember`/`recall` tools back this up.

## Vision (optional)
To let the agent look at your webcam and describe a scene:

```bash
ollama pull qwen2.5vl:7b    # or llava
```
Set `VISION_MODEL=qwen2.5vl:7b` in `.env`, then run with `--vision`:
```bash
python3 agent.py --vision
you> what's on my desk?
```
The `describe_scene` tool captures a frame from your camera and sends it to
the local vision model. Vision stays disabled unless you set `VISION_MODEL`
and pass `--vision`.

## Improvements added
- **Robust tool-call parsing** — the agent now tolerates markdown code fences
  and stray text around its JSON tool calls, so it reliably triggers tools
  instead of returning raw JSON.
- **Friendly device names** — `ha_list_entities` now returns both the entity
  ID and its friendly name (e.g. `light.living_room = "Living Room"`), and you
  can pre-map names in `HA_ENTITY_MAP` so the model finds the right device
  faster.
- **Faster voice confirmations** — yes/no prompts use a shorter 3s window
  (`CONFIRM_RECORD_SECONDS`) instead of the full 5s command window.
- **Wake-word polish** — ignores silence/degenerate transcriptions and adds a
  debounce so it doesn't re-trigger on the wake word's fading audio.

## Professional / operations features
- **Conversation context window** — long sessions stay fast: the agent keeps a
  rolling window of recent messages (`MAX_CONTEXT_MESSAGES`, default 20) and
  compresses older turns into a summary so key preferences aren't lost while
  token usage stays bounded.
- **Session logging** — every interaction, tool call, and reply is written to a
  timestamped `.jsonl` file in `LOG_DIR` (default `logs/`). Secrets (HA token,
  piper paths) are redacted before writing. The current log path is shown at
  startup.
- **Startup config validation** — missing `.env`, unreachable Ollama, unset HA
  credentials, and unavailable vision models are flagged with actionable
  warnings at launch instead of failing mid-use.
- **`--status` health check** — run `python3 agent.py --status` for a summary
  table of every subsystem (Ollama, agent model, Home Assistant, TTS, vision,
  face data).
- **Graceful failures** — Ollama going down mid-session shows a clear message
  and drops only the failed turn; the session continues instead of crashing.
- **Command history** — in text mode you can scroll up/arrow through previous
  inputs like a real REPL (persisted to `history.txt`).
- **Markdown rendering** — the agent's replies are rendered with rich, so
  lists, headings, and code blocks display cleanly.
- **Shell command allow/denylist** — replaces the old fragile `DANGEROUS_PATTERNS`
  string check with real lists: allowlisted commands run without prompting,
  denylisted commands are always blocked, everything else asks for confirmation.
  Configure via `SHELL_ALLOWLIST` / `SHELL_DENYLIST` in `.env`.

### Health check
```bash
python3 agent.py --status
```
Example output: a table showing Ollama reachability, whether your agent model
is installed, Home Assistant authentication, TTS setup, vision availability,
and face-recognition enrollment.

### Session logs
```bash
ls logs/          # one timestamped .jsonl per session
tail -f logs/latest
```

### Agent behavior (system prompt)
A standing system prompt tells the model it is a **terminal engineering agent**:
use its tools rather than describing what it would do, write real runnable
code, think/plan before acting on hard multi-step tasks, search its knowledge
and past sessions before guessing, and research to fill gaps. It's injected
into every new session automatically and is also baked into the model via
`Modelfile`. If you want to tune the agent's personality or strictness, edit
`system_prompt.py` (the runtime prompt) and/or the `SYSTEM` block in
`Modelfile` (the baked-in copy).

### Session memory — see and search past conversations
The agent never forgets what it discussed. Every session is logged, and it can
search all of them at runtime.

```bash
# CLI sanity checks
python3 session_memory.py list
python3 session_memory.py search "porch light"
```

In conversation, the tools are **`search_history`** and **`list_sessions`**:
```
you> go search my past sessions, where did I write "porch light"?
you> what did we do in my last session?  -> it lists sessions, then you can ask it to search
```
This lets the agent find where a word/phrase appeared across every past
conversation, then continue with that context — exactly the "resume a topic I
raised before" workflow.

## Teach it from your own documents (RAG knowledge base)
You can give the agent your own knowledge to answer from — notes, docs, any
plain text. It builds a local searchable index and pulls the relevant chunks
into context when you ask. Everything is local; nothing leaves the machine.

**1. Add a folder of your docs** (text, markdown, csv are loaded by default).
```bash
mkdir -p knowledge
# drop your .md/.txt/.csv files in here, e.g.:
echo 'I prefer coffee over tea.' > knowledge/personal.md
```

**2. (Recommended) enable semantic search** by pulling a small embedding model
once. Until you do, retrieval uses a built-in keyword fallback that already
works offline:
```bash
ollama pull nomic-embed-text
```

**3. Ingest and test:**
```bash
python3 knowledge.py ingest          # index the knowledge/ folder
python3 knowledge.py search "what do I like to drink"
python3 knowledge.py stats           # show the index
```

**4. Use it in conversation.** The agent has tools `kb_search`, `kb_ingest`,
`kb_stats`. Ask something that your notes answer:
```
you> according to my notes, what coffee do I prefer?
```

Settings in `.env`: `KNOWLEDGE_DIR`, `KNOWLEDGE_INDEX`, `EMBED_MODEL`,
`KNOWLEDGE_EXTS`. Note: embedding many large files on a CPU-only machine is
slow — index notes/docs, not your whole disk.

### Let the agent research and feed its own knowledge base
The agent can learn a topic from URLs you give it, save it as a knowledge doc,
ingest it, and remember it — so next time it answers from its own research.

**On-demand (in conversation):**
```
you> research Home Assistant automations \
     urls: https://www.home-assistant.io/docs/automation/
```
This fetches the pages, writes `knowledge/auto/home-assistant-automations.md`,
indexes it, and notes the topic in memory.

**Scheduled auto-learn** (re-fetch every topic in `knowledge/research_seeds.json`):
```bash
python3 research_agent.py auto
```
Add your own topics/seed URLs to `knowledge/research_seeds.json`. For a cron
job, put `research_agent.py auto` on a weekly schedule.

Note: research fetches only the URLs you seed it with (it has no web-searching
key by design). Extend `research_seeds.json` over time and your KB grows in
exactly the topics you care about. Re-ingests are de-duplicated so the index
doesn't bloat.

## Run it as a server (API service)
The same agent can run as an always-on HTTP/API server that other machines on
your network can call — this is what lets you host the AI on one machine and
talk to it from another while voice + Home Assistant live on the server.

```bash
python3 -m server.server                 # text API server, uses .env
python3 -m server.server --host 0.0.0.0  # reachable on the LAN
```

Endpoints (all require `Authorization: Bearer <SERVER_TOKEN>`):
- `GET  /api/health` — subsystem status
- `POST /api/chat`   — `{"text":"..."}` → `{"reply":"..."}`
- `POST /api/stt`    — audio bytes in body → `{"text":"..."}`
- `POST /api/tts`    — `{"text":"..."}` → WAV audio
- `POST /api/reset`  — reset a client's conversation

Example from another machine:
```bash
curl -X POST http://SERVER_IP:8899/api/chat \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"text":"what lights do I have?"}'
```

`SERVER_HOST` (default `0.0.0.0`), `SERVER_PORT` (default `8899`) and
`SERVER_TOKEN` are set in `.env`. **Set a strong `SERVER_TOKEN`** — if it's
empty the server accepts every request.

## Control a separate laptop over SSH (optional)
The server can run shell/file commands on *another* laptop so the AI can
"do anything" there. This is key-based SSH **outbound** from the server — it
does not open an exposed port on the laptop.

1. On the server machine run `client/connect_laptop.sh` — it generates a key and
   prints the public key to install on the laptop's `~/.ssh/authorized_keys`.
2. Fill in `SSH_TARGET`, `SSH_KEY`, `SSH_PORT`, `SSH_ALLOWED_DIRS` in `.env`.
3. Restart the server. It now also exposes tools `ssh_shell`, `ssh_read`,
   `ssh_write`, `ssh_list` that act on the laptop, scoped to `SSH_ALLOWED_DIRS`.

Security: only connect to machines you control, keep the key safe, and scope
`SSH_ALLOWED_DIRS` to the folders the agent is allowed to touch.

## Auto-start at login (systemd user services)
Services running automatically include the API server, face-presence watcher,
and wake-word assistant:

```bash
cd systemd
chmod +x create-services.sh
./create-services.sh            # install + enable + start all
./create-services.sh --server   # only the API server
./create-services.sh --terminal # only presence + wake
./create-services.sh --disable  # stop + disable all
```
# Jean-AI
