# Dotbot nix-env plugin
A plugin for [dotbot](https://github.com/anishathalye/dotbot), which installs packages using the `nix-env` command from the [Nix package manager](https://nixos.org/). 

## Install
```shell
git submodule add git@github.com:DanTheMinotaur/dotbot-nix-env.git
git submodule update --init --recursive

# Pass --plugin-dir dotbot-nix-env to you dotbot command
./install --plugin-dir dotbot-nix-env
```

## Usage

Add the `nixenv` directive to your `install.yaml`. 

Using string values is equivalent to `nix-env -iA <package>`, which will install the latest version available. 
Using a hash `{ <package>: <revision> }` is equivalent `nix-env -iA <package> -f <revision>`.

You can find package revisions here: [https://lazamar.co.uk/nix-versions/](https://lazamar.co.uk/nix-versions/)

### Example config
```yaml
- nixenv:
    packages:
      - nodejs-15_x: 'https://github.com/NixOS/nixpkgs/archive/5c79b3dda06744a55869cae2cba6873fbbd64394.tar.gz'
      - nixpkgs.htop
      - nixpkgs.multitail
```

## Dev Setup

```shell
git clone https://github.com/anishathalye/dotbot.git
pip install -e dotbot/
```

### Live Test
```shell
./dotbot/bin/dotbot -d ./tests/example/ --plugin-dir ./ -c ./tests/example/install.yml
```

### Run Unit Tests
```shell
python -m unittest discover -s tests/ -p '*_test.py'
```