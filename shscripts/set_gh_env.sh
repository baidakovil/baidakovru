#!/bin/bash

# Exit on error
set -e

# Path to env file
ENV_FILE_PATH=".env.sensitive"

echo "Read file content"
ENV_CONTENT=$(cat "$ENV_FILE_PATH")

# Set secret
echo "Setting GitHub Secret ENV_FILE..."
gh secret set ENV_FILE --body "$ENV_CONTENT" --repo baidakovil/baidakovru

echo "✅ Secret ENV_FILE has been set successfully"
echo "Script executed"

# ----------------------------------------
# To manage this, do
# chmod +x ./shscripts/set_gh_env.sh
# ./shscripts/set_gh_env.sh
# ----------------------------------------
