#!/bin/bash

# ==============================================
# FLUTTER INSTALLATION & BUILD SCRIPT FOR NETLIFY
# ==============================================
# This script downloads and installs Flutter SDK in the Netlify build environment
# then builds the Flutter web application.

set -e  # Exit on any error
set -x  # Print commands as they execute (for debugging)

echo "=========================================="
echo "Starting Flutter Web Build Process"
echo "=========================================="

# Save the project directory (where pubspec.yaml is located)
PROJECT_DIR="$PWD"
echo "📂 Project directory: $PROJECT_DIR"
echo "📂 Directory contents:"
ls -la

# Verify pubspec.yaml exists
if [ ! -f "pubspec.yaml" ]; then
  echo "❌ ERROR: pubspec.yaml not found in $PROJECT_DIR"
  exit 1
fi
echo "✅ Found pubspec.yaml"

# Flutter version to install (matches FLUTTER_VERSION in netlify.toml)
FLUTTER_VERSION="${FLUTTER_VERSION:-3.19.0}"
FLUTTER_CHANNEL="stable"

# Installation paths
FLUTTER_HOME="$HOME/flutter"
FLUTTER_BIN="$FLUTTER_HOME/bin"

# Check if Flutter is already installed
if [ ! -d "$FLUTTER_HOME" ]; then
  echo "📦 Installing Flutter SDK version $FLUTTER_VERSION..."
  
  # Clone Flutter repository
  git clone --depth 1 --branch $FLUTTER_VERSION https://github.com/flutter/flutter.git "$FLUTTER_HOME"
  
  echo "✅ Flutter SDK downloaded successfully"
else
  echo "✅ Flutter SDK already installed at $FLUTTER_HOME"
fi

# Add Flutter to PATH
export PATH="$FLUTTER_BIN:$PATH"

# Verify flutter command is available
which flutter || (echo "❌ Flutter not found in PATH"; exit 1)

# Configure Flutter
echo "🔧 Configuring Flutter..."
flutter config --no-analytics
flutter config --enable-web

# Verify Flutter installation
echo "📋 Flutter version information:"
flutter --version

# Quick doctor check (non-verbose)
echo "🏥 Running Flutter doctor..."
flutter doctor

# Return to project directory
cd "$PROJECT_DIR" || (echo "❌ Failed to return to project directory"; exit 1)
echo "📂 Returned to project directory: $PWD"

echo "=========================================="
echo "Building Flutter Web Application"
echo "=========================================="

# Clean previous build
echo "🧹 Cleaning previous build..."
flutter clean || echo "No previous build to clean"

# Get dependencies
echo "📦 Fetching Flutter dependencies..."
flutter pub get

# Build for web
echo "🛠️ Building Flutter web app (release mode)..."
flutter build web --release

# Verify build output
if [ -d "build/web" ]; then
  echo "✅ Build directory created"
  echo "📦 Build contents:"
  ls -la build/web/
  # Ensure Netlify redirects file is present in build output
  if [ -f "web/_redirects" ]; then
    cp web/_redirects build/web/_redirects
    echo "✅ Copied web/_redirects to build/web/_redirects"
  else
    echo "⚠️ web/_redirects not found; Netlify may rewrite JS requests"
  fi
else
  echo "❌ Build failed - no build/web directory created"
  exit 1
fi

echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
