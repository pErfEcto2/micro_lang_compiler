---
name: update-tests-docs
description: Add tests for a feature, update docs/tutor/readme, commit, and push
argument-hint: [feature-description]
---

# Update Tests, Docs, Commit, and Push

## Step 1: Understand what to test

- If `$ARGUMENTS` is provided, use it as the feature description
- Otherwise, ask the user what feature to add tests/docs for

## Step 2: Add tests

**STRICT RULE: Never modify files outside of `tests/`, `docs/`, and `README.md`.**

Read the current source code in `src/` to understand the feature being tested. Then read the existing test files to match their patterns exactly:

- **`tests/test_tokenizer.py`** — Add keyword tokenization tests following the `TestTokenizerWhileKeyword` pattern (test that the tokenizer produces the correct token type for the new keyword/syntax)
- **`tests/test_parser.py`** — Add AST parsing tests with raw tokens + integration tests following the `TestParserWhileStatement`, `TestParserNestedWhile`, and `TestParserWhileIntegration` patterns (test parsing raw token lists and full source strings)
- **`tests/test_compiler.py`** — Add assembly output tests following the `TestCompilerWhileStatement` pattern (test that the compiler emits the correct assembly instructions)
- **`tests/test_main.py`** — Add end-to-end and runtime execution tests following the `TestMainIfStatement` and `TestRuntimeWhileScope` patterns (test the full pipeline from source to execution)

For each test file:
1. Read the file first to understand current imports and class patterns
2. Add new test class(es) matching the naming convention: `TestTokenizer<Feature>`, `TestParser<Feature>`, `TestCompiler<Feature>`, `TestMain<Feature>` / `TestRuntime<Feature>`
3. Update imports as needed

After writing tests, run them with `python -m pytest tests/ -v` and fix any failures.

## Step 3: Update docs

- **`docs/keywords.md`** — Mark the feature as implemented (remove "not implemented" if present), or add a new row to the table
- **`docs/tutor.md`** — Add a section with examples following the existing tutorial style and formatting
- **`README.md`** — Add the feature to the "Language Features" list and optionally update the example program

Read each doc file before editing to match existing style exactly.

## Step 4: Update test.mil

Replace the contents of `tests/test.mil` with a meaningful example program that showcases the new feature alongside existing features.

## Step 5: Commit and push

1. Run `git log --oneline -10` to study the project's commit message style. It is single-line, lowercase, comma-separated phrases, e.g.:
   - `for loop added, tests added, docs updated`
   - `increment/decrement added, tests added, docs updated`
   - `do/while added, tests added, docs updated`
2. Run `git status` and `git diff HEAD` to see exactly what will be committed.
3. Run `git branch --show-current` and `git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null` to detect the current branch and whether it tracks a remote.
4. Stage the touched files explicitly by name (typically `tests/`, `docs/`, `README.md`, `tests/test.mil`, plus any `src/` files that were modified during the session). Do **not** use `git add -A` or `git add .` — list paths.
5. Create the commit with `git commit -m "<subject>"` where `<subject>` matches the style observed in step 1. **Do not** add a `Co-Authored-By` trailer or any other self-attribution. **Do not** use HEREDOC — a single `-m` flag is enough since the message is one line.
6. Push:
   - If the branch tracks an upstream (step 3 succeeded), run `git push`.
   - If not, run `git push -u origin <branch>` to set upstream.
   - If `git remote` is empty, skip the push and tell the user no remote is configured.
7. Print the final commit hash and the push result so the user can confirm.

Safety rules for this step:
- Never `--amend` an existing commit; always create a new one.
- Never push to `main`/`master` with `--force` or `--force-with-lease`.
- If a pre-commit hook fails, fix the underlying issue and create a new commit; do not pass `--no-verify`.
- If `git status` shows files that look unrelated to the feature (e.g. local config, secrets, large binaries), stop and ask the user before staging them.
