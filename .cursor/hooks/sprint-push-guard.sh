#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.command // empty')

if [[ ! "$command" =~ git[[:space:]]+push|gh[[:space:]]+pr[[:space:]]+create ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

gates=""
if [[ -f build.gradle.kts ]]; then
  gates="./gradlew check --no-daemon (or ktlintCheck + test + jacocoTestCoverageVerification)"
elif [[ -f package.json ]]; then
  gates="npm run lint && npm test -- --run && npm run build"
elif [[ -f pyproject.toml ]] || [[ -f requirements.txt ]]; then
  gates="ruff check . && pytest -v"
fi

echo "$(jq -n \
  --arg gates "$gates" \
  '{
    "permission": "ask",
    "user_message": "Confirm quality gates passed before push/PR.",
    "agent_message": ("Sprint push guard: verify lint + tests passed. Gates: " + $gates + ". Branch must be English kebab-case (feat/slug). PR title/body English only.")
  }')"
exit 0
