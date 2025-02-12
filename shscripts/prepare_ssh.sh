#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Load sensitive data from the same directory where the script is executed"
SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR/..")
KEY_PATH="/root/.ssh/github_actions_key"
# Main input data with server credentials SERVER_IP= and SERVER_USERNAME=
source "$SCRIPT_DIR/server.sensitive"

echo "Define variables"
SCRIPT_PATH="$SCRIPT_DIR/generate_ssh_key.sh"
REMOTE_SCRIPT_PATH="/root/generate_ssh_key.sh"
LOCAL_KEY_PATH="$SCRIPT_DIR/id_rsa"
GITHUB_SECRETS_FILE="$PROJECT_ROOT/.env.github-secrets.sensitive"
GITHUB_SECRETS_BACKUP="$PROJECT_ROOT/.env.github-secrets-backup.sensitive"
ENV_FILE_PATH="$PROJECT_ROOT/.env.sensitive"

echo "Copy my public SSH key to a server's authorized keys file"
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id $SERVER_USERNAME@$SERVER_IP

echo "Copy the script to the remote server"
scp $SCRIPT_PATH $SERVER_USERNAME@$SERVER_IP:$REMOTE_SCRIPT_PATH

echo "Set execute permissions on the remote server"
ssh $SERVER_USERNAME@$SERVER_IP "chmod +x $REMOTE_SCRIPT_PATH"

echo "Execute the script on the remote server"
ssh $SERVER_USERNAME@$SERVER_IP "$REMOTE_SCRIPT_PATH"

echo "Copy the private key to the variable on local machine"
SERVER_SSH_KEY=$(ssh $SERVER_USERNAME@$SERVER_IP "cat $KEY_PATH")

echo "Update GitHub secrets"
gh secret set SERVER_SSH_KEY --body "$SERVER_SSH_KEY" --repo baidakovil/baidakovru
gh secret set SERVER_IP --body "$SERVER_IP" --repo baidakovil/baidakovru
gh secret set SERVER_USERNAME --body "$SERVER_USERNAME" --repo baidakovil/baidakovru
gh secret set ENV_FILE --body "$(cat $ENV_FILE_PATH)" --repo baidakovil/baidakovru

echo "Backup current .env.github-secrets.sensitive file"
if [ -f "$GITHUB_SECRETS_FILE" ]; then
    cp "$GITHUB_SECRETS_FILE" "$GITHUB_SECRETS_BACKUP"
fi

echo "Create new .env.github-secrets.sensitive file"
cat > "$GITHUB_SECRETS_FILE" << EOL
# Variables for deployment:
# 
# Server IP address
SERVER_IP=$SERVER_IP
# User for SSH connect
SERVER_USERNAME=$SERVER_USERNAME
# Password for user
SERVER_SSH_KEY=$SERVER_SSH_KEY

# Variables for production:
# 
# File with environment variables
# ENV_FILE="Text of .env.sensitive file here"
EOL

echo "Remove private key from remote server"
ssh $SERVER_USERNAME@$SERVER_IP "rm $KEY_PATH"

echo "Trigger Deploy to Server workflow"
gh workflow run "Deploy to Server" --repo baidakovil/baidakovru

echo "Script executed"

# ----------------------------------------
# This is the single file needed to run the site.
# Project structure matters. Input data is in 
# To manage this, do
# chmod +x /path/to/deploy_site.sh
# /path/to/deploy_site.sh
# ----------------------------------------
