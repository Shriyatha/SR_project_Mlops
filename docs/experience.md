```markdown
# Experience & Lessons Learned

## What Worked Well
- Using `FastAPI` and `Gradio` made API development and UI integration seamless.
- `Pydantic` validation for YAML & TOML configurations ensured data integrity.
- `mkdocs-material` provided an easy-to-maintain documentation setup.

## Challenges Faced
- Handling large audio files led to timeout issues, which we fixed by increasing `httpx` timeouts.
- Ensuring compliance checks work correctly with different accents required additional tuning.

## What I Learned
- Modularizing code and using configuration files (`config.yaml` & `config.toml`) made the system scalable.
- Automating setup with `uv` and `just` greatly simplified deployment.