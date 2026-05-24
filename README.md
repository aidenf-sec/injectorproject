# inject0r 🔴

A prompt injection test harness for evaluating LLM application security.

## What It Does

inject0r automates the process of testing AI applications for prompt injection vulnerabilities.
It sends a battery of known attack techniques against a target LLM (configured with a system prompt),
then uses an LLM-as-judge to automatically evaluate whether each attack succeeded.

## Why

Prompt injection is the [#1 risk in the OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/).
As AI applications are deployed in production, testing their resilience to adversarial input is critical.

## Attack Categories

| Category | Techniques | Targets |
|---|---|---|
| Direct | Simple rule-breaking requests | All |
| Social Engineering | Authority impersonation | All |
| Context Manipulation | Roleplay reframing, context switching, code in fiction | Per-target |
| Obfuscation | Encoding tricks, translation, pseudocode | Per-target |
| Framing | Hypothetical scenarios, translation as helpfulness | Per-target |
| Information Extraction | System prompt leakage | All |

Attacks are target-aware: each target only receives attacks designed for its rule set,
so results reflect genuine defensive capability rather than irrelevant mismatches.

## Quick Start

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/inject0r.git
cd inject0r
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY='your-key-here'

# Run against all targets
python3 inject0r.py

# Run against a specific target
python3 inject0r.py --target secret_keeper
```

## Built-in Targets

- **Secret Keeper** — AI that must protect a password
- **English Only Bot** — AI that must only respond in English
- **No Code Policy Bot** — AI that must refuse to write code

## Output

Results are printed to the console and saved to `reports/results.json` with full
details including attack payloads, target responses, judge evaluations, the
models used for both target and judge, and the scenario (attack profile) applied
to each target. Each attack gets one of three outcomes:
**bypassed** (attack broke the rules), **blocked** (target defended successfully),
or **error** (API/harness failure — excluded from pass rates so they don't inflate
defense statistics).

The `reports/` directory is excluded from Git by default — red team transcripts
can contain system prompts and should be reviewed before sharing.

## How It Works

1. **Target** (`target.py`) — Configurable LLM applications with system prompts
2. **Attacks** (`attacks.py`) — Library of prompt injection techniques
3. **Judge** (`judge.py`) — LLM-as-judge for automated evaluation
4. **Runner** (`inject0r.py`) — Orchestrates tests and generates reports

## Technologies

- Python 3.9+
- Google Gemini API (gemini-3.1-flash-lite-preview)
- LLM-as-judge evaluation pattern

## References

- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- [Simon Willison's Prompt Injection Series](https://simonwillison.net/series/prompt-injection/)
- [Microsoft PyRIT](https://github.com/Azure/PyRIT)
- [Anthropic's Research on AI Safety](https://www.anthropic.com/research)

## Author

Built by [Your Name] as a learning project in AI security research.

## License

MIT
