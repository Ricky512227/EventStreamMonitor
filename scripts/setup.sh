#!/bin/bash
# Setup script for production-ready structure

set -e

echo "Setting up production-ready structure..."

# Create symlinks for common library
echo "Creating symlinks for common library..."
if [ ! -L "services/usermanagement/common" ]; then
    ln -s ../../common services/usermanagement/common
fi
if [ ! -L "services/booking/common" ]; then
    ln -s ../../common services/booking/common
fi
if [ ! -L "services/notification/common" ]; then
    ln -s ../../common services/notification/common
fi
if [ ! -L "services/auth/common" ]; then
    ln -s ../../common services/auth/common
fi

echo "Setup complete!"

