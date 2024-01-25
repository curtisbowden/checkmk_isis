# Checkmk extension for ISIS-MIB

![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/curtisbowden/checkmk_isis?label=version&logo=git&sort=semver)
[![License](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0.html)
![build](https://github.com/curtisbowden/checkmk_isis/workflows/build/badge.svg)
![flake8](https://github.com/curtisbowden/checkmk_isis/workflows/Lint/badge.svg)
![pytest](https://github.com/curtisbowden/checkmk_isis/workflows/pytest/badge.svg)


## Description

 * isis_adjacency discovers and checks the status of IS-IS adjacency for [ISIS-MIB](https://datatracker.ietf.org/doc/html/rfc4444)

## Development

For the best development experience use [VSCode](https://code.visualstudio.com/) with the [Remote Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension. This maps your workspace into a checkmk docker container giving you access to the python environment and libraries the installed extension has.

The file `.devcontainer/devcontainer.json` defines the Remote Container, and within it there are some options that can be commented or uncommented to change the user which is used in the Remote Container as well as if the checkmk service and web gui are setup for testing your plugin. Temporary credentials for the dev container web gui can also be set within the json file.

## CheckMK

Below are a few cmk cli examples that can be useful when developing a cmk plugin

```
# Service scan for exmaple.host
cmk --verbose --perfdata --debug example.host

# Clear prevous then detect plugins for isis_adjacency
cmk --verbose --perfdata --debug -II --detect-plugins=isis_adjacency example.host

# Check discovery for emaple.host
cmk --verbose --perfdata --check-discovery example.host

# Run isis_adjacency plugin on example.host
cmk --verbose --perfdata --plugins=isis_adjacency example.host
```


## Directories

The following directories in this repo are getting mapped into the Checkmk site.

* `agents`, `checkman`, `checks`, `doc`, `inventory`, `notifications`, `pnp-templates`, `web` are mapped into `local/share/check_mk/`
* `agent_based` is mapped to `local/lib/check_mk/base/plugins/agent_based`
* `nagios_plugins` is mapped to `local/lib/nagios/plugins`

## Continuous integration
### Local

To build the package hit `Crtl`+`Shift`+`B` to execute the build task in VSCode.

`pytest` can be executed from the terminal or the test ui.

### Github Workflow

The provided Github Workflows run `pytest` and `flake8` in the same checkmk docker conatiner as vscode.
