import unittest
from unittest.mock import MagicMock, patch
import nixenv
from subprocess import CompletedProcess


class TestNixEnv(unittest.TestCase):

    def test_path_set_success(self):
        set_path = '/usr/bin/nix-env'
        nix = nixenv.NixEnv(set_path)
        self.assertEqual(nix.path, set_path)

        with patch.object(nixenv.NixEnv, 'shell', MagicMock(return_value=CompletedProcess(
                args='which nix-env', returncode=0, stdout=b'/nix/var/profiles/default/bin/nix-env\n'))):
            nix = nixenv.NixEnv()
            self.assertEqual(nix.path, '/nix/var/profiles/default/bin/nix-env')

    def test_path_set_fails(self):
        with patch.object(nixenv.NixEnv, 'shell', MagicMock(return_value=CompletedProcess(
                args='which nix-env', returncode=1, stdout=b''))):
            with self.assertRaises(nixenv.NixEnv.NixEnvException):
                nixenv.NixEnv()

    def test_install_success(self):
        with patch.object(nixenv.NixEnv, 'shell', MagicMock(return_value=CompletedProcess(
            args='', returncode=0, stdout=b'',
            stderr=b"installing 'multitail-7.0.0'\nbuilding "
                   b"'/nix/store/kf5mii1daf658725vxq4vzy9n4y9dfbk-user-environment.drv'...\n"))) as mock:

            nix = nixenv.NixEnv('/usr/bin/nix-env')
            r = nix.install('multitail')
            self.assertEqual(r, "installing 'multitail-7.0.0'")
            args, _ = mock.call_args
            self.assertEqual(args[0], 'nix-env --install multitail')

    def test_install_fails(self):
        mock = MagicMock(return_value=CompletedProcess(
            args='nix-env --install multitail', returncode=1, stdout=b'',
            stderr=b"error: selector 'nonexistance' matches no derivations"))

        with patch.object(nixenv.NixEnv, 'shell', mock):
            with self.assertRaises(nixenv.NixEnv.NixEnvException) as ctx:
                nix = nixenv.NixEnv('/usr/bin/nix-env')
                nix.install('nonexistance')

            self.assertTrue('Unable to install package' in ctx.exception.message)


if __name__ == '__main__':
    unittest.main()
