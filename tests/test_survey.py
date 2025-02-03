import boa
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"
INITIAL_MINT = 1_000_000 * 10**18  # 1M tokens


def test_initial_state(survey, owner, token, reward_amount):
    """Test initial contract state after deployment"""
    print(f"Testing initial state...")
    print(f"Owner: {owner}")
    print(f"Token address: {token.address}")
    print(f"Survey address: {survey.address}")

    assert survey.owner() == owner
    assert survey.reward_token() == token.address
    assert survey.reward_amount() == reward_amount
    assert not survey.paused()

    contract_balance = token.balanceOf(survey.address)
    print(f"Contract token balance: {contract_balance}")
    assert contract_balance >= reward_amount * 10


def test_eligibility_management(survey, owner, alice, bob):
    """Test adding and removing eligible addresses"""
    print(f"Initial state - Alice eligible: {survey.eligible_addresses(alice)}")

    # Add Alice to eligible addresses
    with boa.env.prank(owner):
        survey.add_address(alice)

    assert survey.eligible_addresses(alice)
    print(f"After adding - Alice eligible: {survey.eligible_addresses(alice)}")

    # Try to add from non-owner account
    with boa.env.prank(bob):
        with boa.reverts("!owner"):
            survey.add_address(bob)

    # Remove Alice
    with boa.env.prank(owner):
        survey.remove_address(alice)

    assert not survey.eligible_addresses(alice)


def test_successful_claim(survey, owner, alice, token, reward_amount):
    """Test successful token claim process"""
    initial_balance = token.balanceOf(alice)
    initial_contract_balance = token.balanceOf(survey.address)
    print(
        f"Initial balances - Alice: {initial_balance}, Contract: {initial_contract_balance}"
    )

    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice)

    # Claim tokens
    with boa.env.prank(alice):
        tx = survey.claim()
        print(f"Claim transaction successful: {tx}")

    final_balance = token.balanceOf(alice)
    final_contract_balance = token.balanceOf(survey.address)
    print(
        f"Final balances - Alice: {final_balance}, Contract: {final_contract_balance}"
    )

    assert final_balance == initial_balance + reward_amount
    assert final_contract_balance == initial_contract_balance - reward_amount
    assert not survey.eligible_addresses(alice)


def test_claim_for(survey, owner, alice, bob, token, reward_amount):
    """Test claiming on behalf of another address"""
    initial_alice_balance = token.balanceOf(alice)
    initial_bob_balance = token.balanceOf(bob)
    print(
        f"Initial balances - Alice: {initial_alice_balance}, Bob: {initial_bob_balance}"
    )

    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice)
        print(f"Added Alice to eligible addresses")

    # Bob claims for Alice
    with boa.env.prank(bob):
        tx = survey.claim_for(alice)
        print(f"Claim-for transaction successful: {tx}")

    final_alice_balance = token.balanceOf(alice)
    final_bob_balance = token.balanceOf(bob)
    print(f"Final balances - Alice: {final_alice_balance}, Bob: {final_bob_balance}")

    assert final_alice_balance == initial_alice_balance + reward_amount
    assert final_bob_balance == initial_bob_balance
    assert not survey.eligible_addresses(alice)


def test_paused_functionality(survey, owner, alice):
    """Test pause and unpause functionality"""
    # Make Alice eligible
    with boa.env.prank(owner):
        survey.add_address(alice)
        print("Added Alice to eligible addresses")

        # Pause contract
        survey.pause()
        print("Contract paused")

    assert survey.paused()

    # Try to claim while paused
    with boa.env.prank(alice):
        with boa.reverts("paused"):
            survey.claim()

    print("Claim attempt while paused properly reverted")

    # Unpause and claim
    with boa.env.prank(owner):
        survey.unpause()
        print("Contract unpaused")

    with boa.env.prank(alice):
        tx = survey.claim()
        print(f"Claim after unpause successful: {tx}")


@given(value=st.integers(min_value=1, max_value=INITIAL_MINT))
@settings(
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    deadline=None,
    max_examples=10,
)
def test_token_operations(token, owner, alice, value):
    """Property-based testing of token operations"""
    print(f"Testing with value: {value}")

    initial_balance = token.balanceOf(alice)

    with boa.env.prank(owner):
        token.transfer(alice, value)

    assert token.balanceOf(alice) == initial_balance + value
    print(f"Transfer successful. New balance: {token.balanceOf(alice)}")
