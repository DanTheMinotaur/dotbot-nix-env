import os
import sys
from typing import List

import dotbot


def add_module_to_path():
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    if path not in sys.path:
        sys.path.append(path)


add_module_to_path()

from lib.nixenv import NixEnv


class NixEnvPlugin(dotbot.Plugin):
    _directive = "nixenv"

    def can_handle(self, directive: str) -> bool:
        return directive == self._directive

    def handle(self, directive: str, config: dict) -> bool:
        if not self.can_handle(directive):
            return False

        self._log.action("Installing packages with nix-env")

        nix: NixEnv

        try:
            nix = NixEnv(config.get("nix_path", None))
        except NixEnv.NixEnvException as e:
            self._log.error(e.message)
            return False

        update: bool = config.get("update", False)
        packages: List[str] = config.get("packages", [])

        for package in packages:
            try:
                result = nix.install(package, update=update)
                self._log.action(result.message)
                if result.output:
                    self._log.debug(result.output)
            except NixEnv.NixEnvException as e:
                self._log.error(e.message)
        return True
