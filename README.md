# Dotbot nix-env plugin
A plugin for [dotbot](https://github.com/anishathalye/dotbot) that installs packages using `nix profile` from the [Nix package manager](https://nixos.org/).

## Install
```shell
git submodule add git@github.com:DanTheMinotaur/dotbot-nix-env.git
git submodule update --init --recursive

# Pass --plugin-dir dotbot-nix-env to your dotbot command
./install --plugin-dir dotbot-nix-env
```

## Usage

Add the `nixenv` directive to your `install.yaml`.

### Options

| Option | Type | Default | Description |
|---|---|---|---|
| `packages` | list | `[]` | List of packages to install. Each entry is a flake reference passed directly to `nix profile add`. |
| `update` | bool | `false` | When `true`, already-installed packages will be upgraded via `nix profile upgrade`. |
| `nix_path` | string | auto | Path to `nix-env`. Detected automatically via `which nix-env` if omitted. |

### Package format

Packages are passed directly to `nix profile add`, so any valid flake reference works:

```yaml
# Latest from nixpkgs
- nixpkgs#htop

# Specific nixpkgs branch
- nixpkgs/release-24.05#htop

# Pinned to a specific commit
- github:NixOS/nixpkgs/d73407e8e6002646acfdef0e39ace088bacc83da#htop

# Specific output (e.g. man pages only)
- nixpkgs#bash^man
```

> **Note:** Packages must be installed using a flake reference (e.g. `nixpkgs#htop`) for `update: true` to work. Packages installed via older commands without a flake ref cannot be upgraded and will emit a warning from nix.

### Example config

```yaml
- nixenv:
    update: false
    packages:
      - nixpkgs#htop
      - nixpkgs#multitail
      - nixpkgs/release-24.05#nodejs
      - github:NixOS/nixpkgs/d73407e8e6002646acfdef0e39ace088bacc83da#ripgrep
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
