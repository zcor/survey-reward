import boa
import pytest


@pytest.fixture
def owner():
    return boa.env.generate_address()


@pytest.fixture
def alice():
    return boa.env.generate_address()


@pytest.fixture
def bob():
    return boa.env.generate_address()


@pytest.fixture
def token(owner):
    contract = boa.load_partial("contracts/mocks/MockToken.vy")
    with boa.env.prank(owner):
        token = contract.deploy("Test Token", "TEST", 18)

        # Mint initial supply to owner
        token._mint_for_testing(owner, 1_000_000 * 10**18)
    return token


@pytest.fixture
def reward_amount():
    return 100 * 10**18


@pytest.fixture
def survey(owner, token, reward_amount):
    contract = boa.load_partial("contracts/SurveyAirdrop.vy")
    with boa.env.prank(owner):
        instance = contract.deploy(token.address, reward_amount)

        # Fund contract
        token.transfer(instance.address, reward_amount * 10)
    return instance
