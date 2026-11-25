#!/bin/bash

# Script to clean all .DS_Store files from current directory and subdirectories
# Usage: ./clean-dsstore.sh

echo "Searching for .DS_Store files..."

# Find and remove all .DS_Store files
find . -name ".DS_Store" -type f -print -delete

echo "Cleanup complete!"
