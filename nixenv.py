import subprocess
from typing import List, Dict

import dotbot


class NixEnv:
    class NixEnvException(Exception):
        def __init__(self, message='Error with nix-env'):
            self.message = message
            super().__init__(message)

    def __init__(self, path: str = None):
        self.path = self.path() if path is None else path

    @staticmethod
    def shell(cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, shell=True, capture_output=True)

    @staticmethod
    def __decode(message: bytes, strip: bool = True) -> str:
        message = message.decode('UTF-8')
        if strip:
            message = message.strip()
        return message

    @staticmethod
    def path() -> str:
        r = NixEnv.shell('which nix-env')
        if r.returncode == 0:
            return NixEnv.__decode(r.stdout)
        raise NixEnv.NixEnvException('Unable to find nix-env on PATH')

    def nix_env(self, subcmd: str) -> str:
        cmd = f'nix-env {subcmd}'
        r = self.shell(cmd)
        if r.returncode == 0:
            msg = r.stdout if len(r.stdout) else r.stderr
            return self.__decode(msg, False).split('\n', 1)[0]
        raise NixEnv.NixEnvException(self.__decode(r.stderr))

    def install(self, package: str, rev_path: str = None) -> str:
        cmd = f'--install {package}'
        if rev_path is not None:
            cmd = f'{cmd} --attr -f {rev_path}'

        try:
            return self.nix_env(cmd)
        except NixEnv.NixEnvException as e:
            raise NixEnv.NixEnvException(f'Unable to install package "{package}"; Reason: "{e.message}"')


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
