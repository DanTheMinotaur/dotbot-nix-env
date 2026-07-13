import unittest
from unittest.mock import MagicMock, patch, call
from subprocess import CompletedProcess
from lib.nixenv import NixEnv


def shell_responses(**responses):
    """Return a mock for NixEnv.shell that maps command substrings to CompletedProcess."""

    def side_effect(cmd):
        for key, result in responses.items():
            if key in cmd:
                return result
        return CompletedProcess(args=cmd, returncode=0, stdout=b"", stderr=b"")

    return MagicMock(side_effect=side_effect)


EMPTY_PROFILE = CompletedProcess(
    args="nix profile list --json",
    returncode=0,
    stdout=b'{"elements":{},"version":3}',
    stderr=b"",
)

PROFILE_WITH_MULTITAIL = CompletedProcess(
    args="nix profile list --json",
    returncode=0,
    stdout=b'{"elements":{"multitail":{"active":true,"priority":5,"storePaths":[]}},"version":3}',
    stderr=b"",
)

PROFILE_WITH_HTOP = CompletedProcess(
    args="nix profile list --json",
    returncode=0,
    stdout=b'{"elements":{"htop":{"active":true,"priority":5,"storePaths":[]}},"version":3}',
    stderr=b"",
)


class TestNixEnv(unittest.TestCase):
    def test_path_set_success(self):
        set_path = "/usr/bin/nix-env"
        with patch.object(NixEnv, "shell", shell_responses(**{"profile list": EMPTY_PROFILE})):
            nix = NixEnv(set_path)
            self.assertEqual(nix.path, set_path)

        with patch.object(
            NixEnv,
            "shell",
            shell_responses(
                **{
                    "which nix-env": CompletedProcess(
                        args="which nix-env",
                        returncode=0,
                        stdout=b"/nix/var/profiles/default/bin/nix-env\n",
                    ),
                    "profile list": EMPTY_PROFILE,
                }
            ),
        ):
            nix = NixEnv()
            self.assertEqual(nix.path, "/nix/var/profiles/default/bin/nix-env")

    def test_path_set_fails(self):
        with patch.object(
            NixEnv,
            "shell",
            shell_responses(
                **{
                    "which nix-env": CompletedProcess(
                        args="which nix-env", returncode=1, stdout=b""
                    )
                }
            ),
        ):
            with self.assertRaises(NixEnv.NixEnvException):
                NixEnv()

    def test_install_success(self):
        install_result = CompletedProcess(
            args="",
            returncode=0,
            stdout=b"",
            stderr=b"installing 'multitail-7.0.0'\nbuilding "
            b"'/nix/store/kf5mii1daf658725vxq4vzy9n4y9dfbk-user-environment.drv'...\n",
        )
        mock = shell_responses(
            **{"profile list": EMPTY_PROFILE, "profile add": install_result}
        )

        with patch.object(NixEnv, "shell", mock):
            nix = NixEnv("/usr/bin/nix-env")
            r = nix.install("multitail")
            self.assertEqual(r, "installing 'multitail-7.0.0'")
            last_cmd = mock.call_args[0][0]
            self.assertEqual(last_cmd, "nix profile add multitail")


    def test_install_already_installed_flake_ref(self):
        """nixpkgs#htop and nixpkgs/branch#htop^man should both match 'htop'."""
        mock = shell_responses(**{"profile list": PROFILE_WITH_HTOP})

        with patch.object(NixEnv, "shell", mock):
            nix = NixEnv("/usr/bin/nix-env")
            self.assertIn("already installed", nix.install("nixpkgs#htop"))
            self.assertIn("already installed", nix.install("nixpkgs/release-24.05#htop"))
            self.assertIn("already installed", nix.install("nixpkgs#htop^man"))


    def test_install_already_installed(self):
        mock = shell_responses(**{"profile list": PROFILE_WITH_MULTITAIL})

        with patch.object(NixEnv, "shell", mock):
            nix = NixEnv("/usr/bin/nix-env")
            r = nix.install("multitail")
            self.assertIn("already installed", r)
            # profile add must never be called
            for c in mock.call_args_list:
                self.assertNotIn("profile add", c[0][0])

    def test_install_fails(self):
        mock = shell_responses(
            **{
                "profile list": EMPTY_PROFILE,
                "profile add": CompletedProcess(
                    args="nix profile add nonexistance",
                    returncode=1,
                    stdout=b"",
                    stderr=b"error: selector 'nonexistance' matches no derivations",
                ),
            }
        )

        with patch.object(NixEnv, "shell", mock):
            with self.assertRaises(NixEnv.NixEnvException) as ctx:
                nix = NixEnv("/usr/bin/nix-env")
                nix.install("nonexistance")

            self.assertIn("Unable to install package", ctx.exception.message)


if __name__ == "__main__":
    unittest.main()
