# @version 0.4.0

"""
@title Big Crypto Poll Reward Distributor
@license MIT
@author crv.mktcap.eth
@notice Details: https://curve.substack.com/p/big-crypto-poll-results

         #################
       #####################++++
     ##################+++++++++++++
    +###############++++++++++++++++++++
   ++###############+++++++++++++++++++++++
  +++###############++++++++++++++++++++++++++
 +++++###############+++++++-----++--+++++++++++
 +++++###############++---------------------++++++
 -+++++##############++-----------------------------
--+++++++############++------------------------------
---+++++++##########++++------------------------------
---+++++++++++++++++++++-------------------------------
----++++++++++++++++++++-------------------------------
-----+++++++++++++++++++-------------------------------
---------------+++++++++-------------------------------
------------------+++++--------------------------------
-------------------------------------------------------
 ------------------------------------------------------
 -----------------------------------------------------
 --------------------------------------------------+
 +---------------------------------------------++
  +--------------------------------------+++
   +---------++++++++----------+++++
   ++++++++++++++++++----+++++
    ++++++++++++++++-----+
     ++++++++++++++++++++
      #+++++++++++++++++
       ########++++++++
        ##############
          ##########
"""

from ethereum.ercs import IERC20

import ownable_2step as ownable
import pausable


# ================================================================== #
# ⚙️ Modules
# ================================================================== #

initializes: ownable
exports: (
    ownable.owner,
    ownable.pending_owner,
    ownable.transfer_ownership,
    ownable.accept_ownership,
)

initializes: pausable[ownable := ownable]
exports: (
    pausable.paused,
    pausable.pause,
    pausable.unpause,
)


# ================================================================== #
# 📣 Events
# ================================================================== #

event Claim:
    user: address
    value: uint256


# ================================================================== #
# 💾 Storage
# ================================================================== #

reward_token: public(IERC20)
reward_amount: public(uint256)
eligible_addresses: public(HashMap[address, bool])


# ================================================================== #
# 🚧 Constructor
# ================================================================== #

@deploy
def __init__(reward_token: IERC20, reward_amount: uint256):
    assert (
        reward_amount > 0 and reward_amount <= max_value(uint256) // 2
    ), "!amount"

    ownable.__init__()
    pausable.__init__()
    self.reward_token = reward_token
    self.reward_amount = reward_amount


# ================================================================== #
# 👀 View Functions
# ================================================================== #

@external
@view
def pending_claim_amount(addr: address) -> uint256:
    """
    @notice Pending claim amount
    @param addr Address to check
    @return Amount of tokens received on claim
    """
    if self.eligible_addresses[addr]:
        return self.reward_amount
    return 0


# ================================================================== #
# ✍️ Write Functions
# ================================================================== #

@external
def claim():
    """
    @notice Allows whitelisted addresses to withdraw tokens
    """
    self._claim(msg.sender)


@external
def claim_for(addr: address):
    """
    @notice Allows whitelisted addresses to withdraw tokens
    @param addr Eligible address for claim
    """
    # ownable._check_owner()
    self._claim(addr)


# ================================================================== #
# 👑 Admin Functions
# ================================================================== #

@external
def add_address(addr: address):
    """
    @notice Adds an address to the whitelist
    @param addr Address to add
    """

    ownable._check_owner()
    self.eligible_addresses[addr] = True


@external
def remove_address(addr: address):
    """
    @notice Removes an address from the whitelist
    @param addr Address to remove
    """
    ownable._check_owner()
    self.eligible_addresses[addr] = False


@external
def withdraw_remaining(_token: IERC20):
    """
    @notice Allows owner to withdraw any remaining tokens
    @param _token Token address to withdraw
    """
    ownable._check_owner()
    amount: uint256 = staticcall _token.balanceOf(self)
    assert amount > 0, "!balance"
    assert extcall _token.transfer(msg.sender, amount), "!transfer"


# ================================================================== #
# 🏠 Internal Functions
# ================================================================== #

@internal
def _claim(_user: address):
    pausable._check_unpaused()
    assert self.eligible_addresses[_user], "!address"

    _amount: uint256 = self.reward_amount
    _balance: uint256 = staticcall self.reward_token.balanceOf(self)
    assert _balance >= _amount, "!balance"

    # Update state before transfer
    self.eligible_addresses[_user] = False

    # Transfer tokens to the caller
    assert extcall self.reward_token.transfer(_user, _amount), "!transfer"

    log Claim(_user, self.reward_amount)
