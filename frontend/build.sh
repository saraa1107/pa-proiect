#!/bin/bash

# ==============================================
# FLUTTER INSTALLATION & BUILD SCRIPT FOR NETLIFY
# ==============================================
# This script downloads and installs Flutter SDK in the Netlify build environment
# then builds the Flutter web application.

set -e  # Exit on any error

echo "=========================================="
echo "Starting Flutter Web Build Process"
echo "=========================================="

# Save the project directory (where pubspec.yaml is located)
PROJECT_DIR="$PWD"
echo "📂 Project directory: $PROJECT_DIR"

# Flutter version to install (matches FLUTTER_VERSION in netlify.toml)
FLUTTER_VERSION="${FLUTTER_VERSION:-3.16.5}"
FLUTTER_CHANNEL="stable"

# Installation paths
FLUTTER_HOME="$HOME/flutter"
FLUTTER_BIN="$FLUTTER_HOME/bin"

# Check if Flutter is already installed
if [ ! -d "$FLUTTER_HOME" ]; then
  echo "📦 Installing Flutter SDK version $FLUTTER_VERSION..."
  
  # Create flutter directory
  mkdir -p "$FLUTTER_HOME"
  
  # Clone Flutter repository
  git clone https://github.com/flutter/flutter.git -b $FLUTTER_CHANNEL "$FLUTTER_HOME"
  
  # Checkout specific version
  cd "$FLUTTER_HOME"
  git checkout $FLUTTER_VERSION
  
  echo "✅ Flutter SDK downloaded successfully"
else
  echo "✅ Flutter SDK already installed at $FLUTTER_HOME"
fi

# Add Flutter to PATH
export PATH="$FLUTTER_BIN:$PATH"

# Configure Flutter
echo "🔧 Configuring Flutter..."
flutter config --no-analytics
flutter config --enable-web

# Verify Flutter installation
echo "📋 Flutter version information:"
flutter --version

# Run Flutter doctor to check setup
echo "🏥 Running Flutter doctor..."
flutter doctor -v

# Return to project directory
cd "$PROJECT_DIR"
echo "📂 Returned to project directory: $PWD"

echo "=========================================="
echo "Building Flutter Web Application"
echo "=========================================="

# Get dependencies
echo "📦 Fetching Flutter dependencies..."
flutter pub get

# Build for web
echo "🛠️ Building Flutter web app (release mode)..."
flutter build web --release --web-renderer html

echo "=========================================="
echo "✅ Build completed successfully!"
echo "=========================================="
