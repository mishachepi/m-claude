# Reusable Directives

Short phrases that reliably change how a coding agent plans, investigates and reports. Paste them
into a prompt, a CLAUDE.md, or a skill. Each comes with its reason — keep the reason when pasting,
Claude generalizes from it.

## Standing directives — good for CLAUDE.md

**Prefer mature, maintained libraries over custom implementations.**
Less own code to maintain, and the model has almost certainly seen the library in training, so it
writes correct code without researching docs and sources first.

**Fix the cause, not the symptom.**
Points the investigation at the source of the problem, so the fix is not a patch over the hole that
has to be re-checked later.

**Prefer checking sources over knowledge from training.**
Read the actual docs, library code and data before relying on memory. Stronger models with more
reasoning check more often on their own, but still need the push.

**Name explicitly the assumptions that change how the solution behaves.**
The model always makes some decisions on its own and does not always say so. Make them visible.

**Report what was verified and what could not be verified.**
Separates claims backed by a check from claims built on the model's own picture of the system.

## Task prompts — paste when planning or refactoring

**Find implicit state machines and propose a version with the state made explicit.**
Surfaces flag-driven code, transition logic spread across functions, and places with no clear
status field.

## Using them in a review

When auditing a prompt for a coding agent (Mode 2), check whether a missing standing directive
would close a gap the prompt leaves open — for example, a debugging prompt without "fix the cause"
or a research prompt without "report what was verified". Suggest only the ones that fit the task.
