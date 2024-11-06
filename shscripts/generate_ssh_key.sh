#!/bin/bash

# Set variables
KEY_NAME="github_actions_key"
KEY_PATH="$HOME/.ssh/$KEY_NAME"
KEY_COMMENT="key for GitHub Actions"

# Generate the SSH key
ssh-keygen -t rsa -b 4096 -C "$KEY_COMMENT" -f "$KEY_PATH" -N ""

# Add the public key to authorized_keys
cat "${KEY_PATH}.pub" >> "$HOME/.ssh/authorized_keys"

# Set correct permissions
chmod 700 "$HOME/.ssh"
chmod 600 "$HOME/.ssh/authorized_keys"

# Print the private key
echo "Here's your private key. Copy this entire output, including the BEGIN and END lines, into your GitHub secret:"
echo "----------------------------------------"
cat "$KEY_PATH"
echo "----------------------------------------"

# Print instructions
echo "The public key has been added to ~/.ssh/authorized_keys"
echo "The private key above should be set as your GitHub secret named SERVER_SSH_KEY"
echo "Keep this key secure and do not share it publicly!"

# Optional: remove the private key file for security
# Uncomment the next line if you want to remove the private key file after displaying it
# rm "$KEY_PATH"