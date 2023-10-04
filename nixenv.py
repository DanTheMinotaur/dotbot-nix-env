import os
import sys
from typing import List, Dict

import dotbot


def add_module_to_path():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    if path not in sys.path:
        sys.path.append(path)


add_module_to_path()

from lib.nixenv import NixEnv


class NixEnvPlugin(dotbot.Plugin):
    _directive = 'nixenv'

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, config: Dict) -> bool:
        if not self.can_handle(directive):
            return False

        self._log.info('Installing packages with nix-env')

        nix = NixEnv(config.get('nix_path', None))

        packages: List[str, Dict] = config.get('packages', [])

        for package in packages:
            try:
                revision = None
                if isinstance(package, dict):
                    package, revision = next(iter(package.items()))

                nix.install(package, revision)
                msg = f'Installed {package}'
                if revision:
                    msg += f"; Revision: {revision}"

                self._log.info(msg)
            except NixEnv.NixEnvException as e:
                self._log.error(e.message)
        return True
