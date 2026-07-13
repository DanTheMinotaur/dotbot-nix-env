import json
import subprocess
from typing import NamedTuple


class NixEnv:
    class NixEnvException(Exception):
        def __init__(self, message="Error with nix-env"):
            self.message = message
            super().__init__(message)

    class InstallResult(NamedTuple):
        message: str
        output: str

    def __init__(self, path: str = None):
        self.path = self.path() if path is None else path
        r = self.shell("nix profile list --json")
        self._installed = set(json.loads(r.stdout).get("elements", {}).keys()) if r.returncode == 0 else set()

    @staticmethod
    def shell(cmd: str) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, shell=True, capture_output=True)

    @staticmethod
    def __decode(message: bytes, strip: bool = True) -> str:
        message = message.decode("UTF-8")
        if strip:
            message = message.strip()
        return message

    @staticmethod
    def path() -> str:
        r = NixEnv.shell("which nix-env")
        if r.returncode == 0:
            return NixEnv.__decode(r.stdout)
        raise NixEnv.NixEnvException("Unable to find nix-env on PATH")

    @staticmethod
    def pname(package: str) -> str:
        return package.split("#")[-1].split("^")[0]

    def nix_env(self, subcmd: str) -> str:
        cmd = f"nix {subcmd}"
        r = self.shell(cmd)
        if r.returncode == 0:
            msg = r.stdout if len(r.stdout) else r.stderr
            return self.__decode(msg, False)
        raise NixEnv.NixEnvException(self.__decode(r.stderr))

    def is_installed(self, package: str) -> bool:
        return self.pname(package) in self._installed

    def upgrade(self, package: str) -> "NixEnv.InstallResult":
        bare = self.pname(package)
        try:
            output = self.nix_env(f"profile upgrade {bare}")
        except NixEnv.NixEnvException as e:
            raise NixEnv.NixEnvException(
                f'Unable to upgrade package "{package}"; Reason: "{e.message}"'
            )

        first_line = output.split("\n", 1)[0]
        if first_line.startswith("upgrading "):
            parts = first_line.split("' to '")
            if len(parts) == 2 and parts[0].split("from flake '")[-1] == parts[1].rstrip("'"):
                message = f'Package "{package}" is already up to date'
            else:
                message = f'Package "{package}" upgraded successfully'
        else:
            message = f'Package "{package}" is already up to date'

        return NixEnv.InstallResult(message=message, output=output)

    def install(self, package: str, update: bool = False) -> "NixEnv.InstallResult":
        if self.is_installed(package):
            if update:
                return self.upgrade(package)
            return NixEnv.InstallResult(
                message=f'Package "{package}" is already installed', output=""
            )

        try:
            output = self.nix_env(f"profile add {package}")
        except NixEnv.NixEnvException as e:
            raise NixEnv.NixEnvException(
                f'Unable to install package "{package}"; Reason: "{e.message}"'
            )

        return NixEnv.InstallResult(
            message=f'Package "{package}" installed successfully', output=output
        )
