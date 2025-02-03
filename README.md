# Survey Token Claim

A token reward distribution for participants in the Big Crypto Survey (https://curve.substack.com/p/big-crypto-poll-results).

## Quick Start Guide

### Check Your Eligibility

1. Visit Fraxscan and connect your wallet
2. Go to the contract: [contract_address]
3. Under "Read Contract", find the `eligible_addresses` function
4. Enter your wallet address to check if you're eligible for the claim

### Claim Your Reward

If you're eligible, you can claim your tokens in two ways:

#### Option 1: Through Etherscan
1. Visit the contract on Fraxscan: [contract_address]
2. Connect your wallet
3. Under "Write Contract", click "claim"
4. Confirm the transaction in your wallet

#### Option 2: Direct Contract Interaction
```vyper
// Call the claim function from an eligible address
function claim() external
```

**Note**: After claiming, your address will no longer be eligible for future claims.

## Technical Documentation

### Contract Overview

This contract implements a token distribution system for survey participants, featuring:
- One-time token claims for whitelisted addresses
- Owner-controlled address management
- Pausable functionality for emergency stops
- Two-step ownership transfer for security

### Core Functions

```vyper
claim() external
    // Allows eligible addresses to claim their reward tokens

claim_for(addr: address) external
    // Allows claiming on behalf of eligible addresses

add_address(addr: address) external
    // Owner function to add eligible addresses

remove_address(addr: address) external
    // Owner function to remove addresses from eligibility
```

### Architecture

The contract relies on several [Snekmate](https://github.com/pcaversaccio/snekmate) modules:
- [Ownable2Step](https://github.com/pcaversaccio/snekmate/blob/main/src/snekmate/auth/ownable_2step.vy) for secure ownership management
- [Pausable](https://github.com/pcaversaccio/snekmate/blob/main/src/snekmate/utils/pausable.vy) module for emergency controls
- [ERC20](https://github.com/pcaversaccio/snekmate/blob/main/src/snekmate/tokens/erc20.vy) mock for testing

### Security Features

1. **Access Control**
   - Owner-only functions for address management
   - Two-step ownership transfer process

2. **Safety Checks**
   - Balance verification before transfers
   - Single-claim enforcement
   - Pausable functionality for emergency situations

3. **Anti-Griefing**
   - No loops in core functions
   - Gas-efficient storage layout

### Development

#### Local Setup
```bash
# Clone repository
git clone [repository_url]

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/
```

#### Testing
The contract includes comprehensive test coverage:
- Unit tests for core functionality
- Integration tests for token interactions
- Security tests for access control
- Fuzzing tests for edge cases

### Deployment

This contract is deployed on:
- Fraxtal Mainnet: [contract_address]
- Token Contract: [token_address]

### Parameters

- Reward Amount: [X] tokens per claim
- Token: [TOKEN_NAME]([TOKEN_SYMBOL])
- Owner: [OWNER_ADDRESS]
