# scion

Skills for agents running in a [scion](https://github.com/mishachepi/scion) mesh.

Doctrine: **the agent's template is its persistent memory.** The template directory
(`.scion/templates/<template>/`) survives `scion delete` + respawn; the agent's home does not.

## Skills

| Skill | Purpose |
|---|---|
| `scion-learn` | Capture a durable session lesson into the agent's template (`lessons.md`, or `agents.md` for identity changes) — never into the ephemeral home. |
