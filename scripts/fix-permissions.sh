#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Fixing permissions for all shell scripts...${NC}"

# Find all .sh files in the project (excluding venv and node_modules)
scripts=$(find . -name "*.sh" -type f -not -path "./backend/venv/*" -not -path "./frontend/node_modules/*" -not -path "./.git/*")

count=0
for script in $scripts; do
    # Check if script is already executable
    if [[ ! -x "$script" ]]; then
        echo -e "${YELLOW}Making executable: $script${NC}"
        chmod +x "$script"
        ((count++))
    else
        echo -e "${GREEN}Already executable: $script${NC}"
    fi
done

if [[ $count -eq 0 ]]; then
    echo -e "${GREEN}All scripts already have proper permissions!${NC}"
else
    echo -e "${GREEN}Fixed permissions for $count script(s).${NC}"
fi

echo -e "${YELLOW}Summary of all shell scripts:${NC}"
find . -name "*.sh" -type f -not -path "./backend/venv/*" -not -path "./frontend/node_modules/*" -not -path "./.git/*" -exec ls -la {} \;
