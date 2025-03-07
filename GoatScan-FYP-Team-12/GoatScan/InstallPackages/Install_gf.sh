#!/bin/bash

# Install Go
echo "Installing Go..."
GO_VERSION="1.20.4"  # Specify the desired Go version
wget https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
rm go${GO_VERSION}.linux-amd64.tar.gz

# Set Go environment variables (Execute whenever gf is used)
echo "Setting Go environment variables..."
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go
export PATH=$PATH:$GOPATH/bin

# Install gf tool
echo "Installing gf tool..."
go install github.com/tomnomnom/gf@latest

# Set up gf patterns
echo "Setting up gf patterns..."
mkdir ~/.gf
git clone https://github.com/1ndianl33t/Gf-Patterns.git # Upload our pattern to Github and change this
sudo cp ~/Gf-Patterns/*.json ~/.gf #Change "Gf-Patterns accordingly as well"

# Update shell configuration
echo "Updating shell configuration..."
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
echo 'export GOPATH=$HOME/go' >> ~/.bashrc
echo 'export PATH=$PATH:$GOPATH/bin' >> ~/.bashrc
echo 'source $HOME/.gf/gf-completion.bash' >> ~/.bashrc

echo "Installation completed successfully!"
echo "Please restart your shell or run 'source ~/.bashrc' to start using the gf tool."


# 1) Make script executable:
#   chmod +x install_gf.sh

# 2) Run Script
#   ./install_gf.sh
