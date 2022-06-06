"""


Convex Contract

"""

from convex_api.utils import to_address


class Contract:
    def __init__(self, convex):
        self._convex = convex
        self._name = None
        self._address = None
        self._owner_address = None

    def load(self, name=None, address=None, owner_address=None):

        if name:
            address = self.resolve_address(name)
            owner_address = self.resolve_owner_address(name)
            self._name = name

        if address is None:
            raise ValueError('no contract found')

        if owner_address is None:
            owner_address = address

        self._address = address
        self._owner_address = owner_address
        return self._address

    def deploy(self, account, text=None, filename=None, name=None, owner_account=None):
        if filename:
            with open(filename, 'r') as fp:
                text = fp.read()
        if text is None:
            raise ValueError('You need to provide a contract filename or text to deploy')
        deploy_line = f"""
(deploy
    (quote
        (do
            {text}
        )
    )
)
    """
        result = self._convex.send(deploy_line, account)
        if result and 'value' in result:
            address = to_address(result["value"])
            if name:
                if owner_account is None:
                    owner_account = account
                self._convex.registry.register(name, address, owner_account)
            return address

    def register(self, name, address, account):
        return self._convex.registry.register(name, address, account)

    def send(self, transaction, account):
        if not self._address:
            raise ValueError(f'No contract address found for {self._name}')
        return self._convex.send(f'(call #{self._address} {transaction})', account)

    def query(self, transaction, account_address=None):
        if not self._address:
            raise ValueError(f'No contract address found for {self._name}')
        if account_address is None:
            account_address = to_address(account_address)
        if account_address is None:
            account_address = self._address
        return self._convex.query(f'(call #{self._address} {transaction})', account_address)

    def resolve_address(self, name):
        return self._convex.registry.resolve_address(name)

    def resolve_owner_address(self, name):
        return self._convex.registry.resolve_owner(name)

    @property
    def is_registered(self):
        return self._address is not None

    @property
    def address(self):
        return self._address

    @property
    def owner_address(self):
        return self._owner_address

    @property
    def name(self):
        return self._name
