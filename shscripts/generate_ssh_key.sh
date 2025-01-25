#!/bin/bash

# Set variables
KEY_PATH="/root/.ssh/github_actions_key"
KEY_COMMENT="key for GitHub Actions"

# Generate the SSH key
ssh-keygen -t rsa -b 4096 -C "$KEY_COMMENT" -f "$KEY_PATH" -N ""

# Add the public key to authorized_keys
cat "${KEY_PATH}.pub" >> "/root/.ssh/authorized_keys"

# Set correct permissions
chmod 700 "/root/.ssh"
chmod 600 "/root/.ssh/authorized_keys"

# Print the private key
echo "Here's your private key. Copy this entire output, including the BEGIN and END lines, into your GitHub secret:"
echo "----------------------------------------"
cat "$KEY_PATH"
echo "----------------------------------------"

# Print instructions
echo "The public key has been added to ~/.ssh/authorized_keys"
echo "The private key above should be set as your GitHub secret named SERVER_SSH_KEY"
echo "Keep this key secure and do not share it publicly!"

# ----------------------------------------
# To manage this, do
# scp ~/git/baidakovru/shscripts/generate_ssh_key.sh root@ip.ip.ip.ip:/root/generate_ssh_key.sh
# ssh user@remote_server
# chmod +x /root/generate_ssh_key.sh
# /root/generate_ssh_key.sh
# copy the private key to the clipboard and paste it into the GitHub secret
# ----------------------------------------
