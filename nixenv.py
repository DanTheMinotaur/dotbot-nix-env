from lib.nixenv import NixEnv
from typing import List, Dict

import dotbot


class NixEnvPlugin(dotbot.Plugin):
    _directive = 'nixenv'

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, config: Dict) -> bool:
        if not self.can_handle(directive):
            return False

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
