#!/usr/bin/env bash

echo "=== Ollama Runtime Status ==="

if ss -ltn '( sport = :11434 )' | grep -q 11434; then
  echo "Ollama serving: yes"
  echo

  echo "Process:"
  ps -ef | grep -E '[o]llama serve' || true
  echo

  echo "Models:"
  ollama list || echo "failed to list models"

else
  echo "Ollama serving: no"
fi
