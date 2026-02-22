# Installing refgenie

!!! warning "Refgenie is not distributed via regular PyPi just yet (Transitionary Period and Command Mismatch)"

    We are currently in a transitionary period where `refgenie1` will supersede the original `refgenie` package on PyPI. During this transition:

    - **Package Installation**: You must install `refgenie1` (not `refgenie`)
    - **Command Usage**: You must use the `refgenie1` command (not `refgenie`)
    - **Documentation**: All commands in this documentation are written as `refgenie` for future-proofing, but you need to substitute `refgenie1` in practice

Download and install the wheel from any release found here: <https://github.com/refgenie/refgenie1/releases>

```bash
pip install refgenie1-*.whl
```

## Verify installation

```bash
refgenie1 --version
```

## Optional extras

Install with dashboard support (local web UI for browsing assets):

```bash
pip install refgenie1[dash]
```

Install with server support (includes dash plus background scheduling):

```bash
pip install refgenie1[server]
```

### Development install

To install from a local clone for development:

```bash
pip install -e ".[dash]"
```

## Next steps

Configure refgenie!

For more information on how to configure refgenie, see the [Configuration documentation](configuration.md).