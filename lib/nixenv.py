import subprocess


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

