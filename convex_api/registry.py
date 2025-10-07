"""

    ConvexRegistry

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from convex_api.api import API

import logging

from convex_api.account import Account
from convex_api.exceptions import ConvexAPIError

logger = logging.getLogger(__name__)

QUERY_ACCOUNT_ADDRESS = 9


class Registry:

    def __init__(self, convex: API):
        self._convex = convex
        self._address = None
        self._items: dict[str, tuple[int, int] | None] = {}

    def is_registered(self, name: str):
        return self.item(name) is not None

    def item(self, name: str):
        if name not in self._items:
            result = self._convex.query(f'(*registry*/read (symbol "{name}"))', QUERY_ACCOUNT_ADDRESS)
            logger.debug(f'read result: {result}')
            self._items[name] = result.value
        return self._items[name]

    def clear(self):
        self._items = {}
        self._address = None

    def register(self, name: str, contract_address: int, account: Account):
        """Register a contract in the CNS.

        If the name doesn't exist, creates it with [contract_address, caller_address, nil, nil].
        If it exists, updates the value (first element) to contract_address.
        """
        try:
            # Check if entry exists
            existing = self._convex.query(f'(resolve (symbol "{name}"))', QUERY_ACCOUNT_ADDRESS)

            if existing.value is None:
                # Create new entry: [value, controller, metadata, child]
                # Controller defaults to caller (*address* in create function)
                result = self._convex.send(f'(*registry*/create (symbol "{name}") #{contract_address})', account)
                logger.debug(f'create result: {result}')
            else:
                # Update existing entry's value
                result = self._convex.send(f'(*registry*/update (symbol "{name}") #{contract_address})', account)
                logger.debug(f'update result: {result}')

            if result and hasattr(result, 'value'):
                # Clear cache and fetch updated record
                self._items.pop(name, None)
                item = self.item(name)
                return item
        except ConvexAPIError as e:
            logger.error(f'CNS registration error for {name}: {e}')
            raise

    def resolve_owner(self, name: str) -> int | None:
        """Resolve the controller (owner) of a CNS entry."""
        item = self.item(name)
        if item:
            return item[1]

    def resolve_address(self, name: str) -> int | None:
        """Resolve the address (value) of a CNS entry."""
        item = self.item(name)
        if item:
            return item[0]
