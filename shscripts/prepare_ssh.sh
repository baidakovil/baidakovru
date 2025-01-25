#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Load sensitive data from the same directory where the script is executed"
SCRIPT_DIR=$(dirname "$0")
KEY_PATH="/root/.ssh/github_actions_key"
source "$SCRIPT_DIR/server.sensitive"

echo "Define variables"
SCRIPT_PATH="$SCRIPT_DIR/generate_ssh_key.sh"
REMOTE_SCRIPT_PATH="/root/generate_ssh_key.sh"
LOCAL_KEY_PATH="$SCRIPT_DIR/id_rsa"

echo "Copy my public SSH key to a server's authorized keys file"
# ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
ssh-copy-id $USR@$IP

echo "Copy the script to the remote server"
scp $SCRIPT_PATH $USR@$IP:$REMOTE_SCRIPT_PATH

echo "Set execute permissions on the remote server"
ssh $USR@$IP "chmod +x $REMOTE_SCRIPT_PATH"

echo "Execute the script on the remote server"
ssh $USR@$IP "$REMOTE_SCRIPT_PATH"

echo "Copy the private key to the variable on local machine"
PRIVATE_KEY=$(ssh $USR@$IP "cat $KEY_PATH")

echo "Set the GitHub secret"
gh secret set SERVER_SSH_KEY -body "$PRIVATE_KEY" --repo baidakovil/baidakovru

echo "Save the private key in the server.sensitive file"
echo "SERVER_SSH_KEY=\"$PRIVATE_KEY\"" >> "$SCRIPT_DIR/server.sensitive"

echo "Save the private key in the server.sensitive file"
ssh $USR@$IP "rm $KEY_PATH"

echo "Script executed"

# ----------------------------------------
# To manage this, do
# chmod +x /path/to/automate_ssh_key.sh
# /path/to/automate_ssh_key.sh
# ----------------------------------------
