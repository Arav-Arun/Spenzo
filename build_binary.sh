#!/bin/bash
# Spenzo Binary Compiler
# This script bundles the entire Spenzo MCP agent into a single, closed-source executable 
# using PyInstaller. Users can run the resulting binary natively without needing the source code.

echo "📦 Installing PyInstaller..."
uv pip install pyinstaller

echo "🔨 Compiling Spenzo into a single binary..."
# Use --onefile to create a single executable
# Use --name to name the output binary
uv run pyinstaller --onefile --name spenzo main.py

echo "✅ Build Complete!"
echo "Your secure, closed-source Spenzo executable is located in the new 'dist/' folder."
echo "You can now distribute this binary directly to users."
