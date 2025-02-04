import boa
import pytest


def test_withdraw_remaining_success(survey, token, owner, reward_amount):
    """Test successful withdrawal of remaining tokens by owner"""
    initial_owner_balance = token.balanceOf(owner)
    initial_contract_balance = token.balanceOf(survey.address)

    print(
        f"Initial balances - Owner: {initial_owner_balance}, Contract: {initial_contract_balance}"
    )

    with boa.env.prank(owner):
        tx = survey.withdraw_remaining(token.address)
        print(f"Withdrawal transaction successful: {tx}")

    final_owner_balance = token.balanceOf(owner)
    final_contract_balance = token.balanceOf(survey.address)

    print(
        f"Final balances - Owner: {final_owner_balance}, Contract: {final_contract_balance}"
    )

    # Verify balances
    assert final_owner_balance == initial_owner_balance + initial_contract_balance
    assert final_contract_balance == 0


def test_withdraw_remaining_non_owner(survey, token, alice):
    """Test withdrawal attempt by non-owner"""
    with boa.env.prank(alice):
        with boa.reverts("!owner"):
            survey.withdraw_remaining(token.address)


def test_withdraw_remaining_zero_balance(survey, token, owner):
    """Test withdrawal attempt when contract has no tokens"""
    # First withdraw all tokens
    with boa.env.prank(owner):
        survey.withdraw_remaining(token.address)

    # Try to withdraw again
    with boa.env.prank(owner):
        with boa.reverts("!balance"):
            survey.withdraw_remaining(token.address)


def test_withdraw_remaining_different_token(survey, token, owner):
    """Test withdrawing a different token than the reward token"""
    # Deploy another token
    other_token = boa.load_partial("contracts/mocks/MockToken.vy")
    with boa.env.prank(owner):
        other = other_token.deploy("Other", "OTH", 18)
        # Don't fund the contract with this token

    # Try to withdraw the unfunded token
    with boa.env.prank(owner):
        with boa.reverts("!balance"):
            survey.withdraw_remaining(other.address)


@pytest.mark.parametrize("token_amount", [1, 1000, 1_000_000 * 10**18])
def test_withdraw_remaining_various_amounts(survey, token, owner, token_amount):
    """Test withdrawing different token amounts"""
    # Reset token balance
    with boa.env.prank(owner):
        survey.withdraw_remaining(token.address)
        # Fund with test amount
        token._mint_for_testing(owner, token_amount)
        token.transfer(survey.address, token_amount)

    initial_owner_balance = token.balanceOf(owner)

    with boa.env.prank(owner):
        survey.withdraw_remaining(token.address)

    assert token.balanceOf(owner) == initial_owner_balance + token_amount
    assert token.balanceOf(survey.address) == 0
