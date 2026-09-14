# Clone the repo locally (or navigate to your existing local clone)
git clone https://github.com/vmainamc-hub/digitpulse1.git
cd digitpulse1

# Checkout the branch
git checkout liquidity-intelligence-v3

# Pull the exact commit directly from the downloaded bundle
git pull /path/to/downloaded/v4-changes.bundle liquidity-intelligence-v3

# Verify the commit SHA matches
git log -1 --oneline
# You will see: bdfc7b5 Integrate Authoritative Liquidity Model V4 with 12 core invariants and verification suite

# Push using your local GitHub credentials
git push origin liquidity-intelligence-v3