$ErrorActionPreference = "Stop"

Write-Host "📦 Installing maru-deep-pro-search..."
python -m pip install maru-deep-pro-search

Write-Host "🚀 Running setup wizard..."
maru-deep-pro-search setup

Write-Host "✅ Done! Your AI agent is now configured."
