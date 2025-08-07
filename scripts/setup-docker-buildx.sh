#!/bin/bash

# Setup Docker Buildx for Multi-Platform Builds
# This ensures consistent architecture builds across different development machines

set -e

echo "🔧 Setting up Docker Buildx for multi-platform builds..."

# Create a new buildx builder instance if it doesn't exist
if ! docker buildx inspect citycamp-builder >/dev/null 2>&1; then
    echo "📦 Creating new buildx builder: citycamp-builder"
    docker buildx create --name citycamp-builder --driver docker-container --bootstrap
    echo "✅ Created buildx builder: citycamp-builder"
else
    echo "✅ Buildx builder already exists: citycamp-builder"
fi

# Use the builder
echo "🔄 Switching to citycamp-builder..."
docker buildx use citycamp-builder

# Verify the builder supports the platforms we need
echo "🔍 Verifying supported platforms..."
docker buildx inspect --bootstrap

echo ""
echo "✅ Docker Buildx setup complete!"
echo ""
echo "💡 Usage examples:"
echo "   # Build for production (AMD64):"
echo "   docker buildx build --platform linux/amd64 -t myimage:latest ."
echo ""
echo "   # Build for both architectures:"
echo "   docker buildx build --platform linux/amd64,linux/arm64 -t myimage:latest ."
echo ""
echo "   # Build and push directly:"
echo "   docker buildx build --platform linux/amd64 --push -t myimage:latest ."
