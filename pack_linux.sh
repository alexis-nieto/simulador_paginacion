#!/bin/bash

# Define the output name
DIST_DIR="simulador_paginacion_dist"
ARCHIVE_NAME="simulador_paginacion_linux.tar.gz"

# Create a temporary distribution directory
echo "Creating distribution directory..."
mkdir -p "$DIST_DIR"

# Copy essential files
echo "Copying files..."
cp main.py "$DIST_DIR/"
cp memory_manager.py "$DIST_DIR/"

# Create the tarball
echo "Compressing into $ARCHIVE_NAME..."
tar -czvf "$ARCHIVE_NAME" "$DIST_DIR"

# Clean up
echo "Cleaning up..."
rm -rf "$DIST_DIR"

echo "Done! Package created: $ARCHIVE_NAME"
