# Ansible Workspace

This serves as a monolithic repository for the Grafeas Group Ansible configuration scripts.

## Setup

Once fully cloned down (see [Submodules](#submodules) below), ensure you have Python 3.8.0 (or later) installed locally. Then there are a few more setup steps before we get started:

- Setup and activate a virtualenv with `venv`
- Upgrade `pip`
- Install `pip-tools`
- Sync up the installed packages in the virtualenv with the ones declared in `requirements.txt`

Executing the above steps from the shell would look like this:

```shell
~/src/ansible-workspace $ python3 -m venv ./venv
~/src/ansible-workspace $ source ./venv/bin/activate
(venv) ~/src/ansible-workspace $ pip install --upgrade pip
(venv) ~/src/ansible-workspace $ pip install pip-tools
(venv) ~/src/ansible-workspace $ pip-sync requirements.txt
```

Now you're ready to go!

## Usage

By convention, from the Ansible ecosystem, `site.yml` is the default build-the-world playbook. There are a few other playbooks defined in this repository, but any playbook can be invoked like so:

```
(venv) ~/src/ansible-workspace $ export ANSIBLE_REMOTE_USER='my_server_username'
(venv) ~/src/ansible-workspace $ ssh-add ~/.ssh/id_rsa
(venv) ~/src/ansible-workspace $ ansible-playbook ./site.yml --inventory ./inventory --ask-become-pass
```

This makes a few assumptions:

- SSH connectivity to the target servers is defined in the inventory (IP address, port, etc.)
- SSH private key authentication is setup (perhaps with `ssh-agent`?)
- SSH username is defined in the environment variable `ANSIBLE_REMOTE_USER` or the inventory as an Ansible var, `ansible_user`
- The account password for the remote user is known and can be typed when prompted for a sudo password

## Directory structure

```
~/src/ansible-workspace/
├── dev-requirements.in
├── dev-requirements.txt
├── get_password_hash.yml
├── inventory/
├── README.md
├── requirements.in
├── requirements.txt
├── roles/
├── site.yml
└── upgrade_bots.yml
```

### Dependency tracking

Overall, this repository uses [the `requirements.txt` approach][requirements.txt] to tracking python dependencies, facilitated with [`venv`][venv] and [`pip-tools`][pip-tools]. Dependencies in `requirements.txt` (and `dev-requirements.txt`) should represent a snapshot of all resolved versions of packages and all dependencies underneath. Since that is quite cumbersome to manually curate, we use `pip-tools` to manage it.

This means your entire development environment can be installed with `pip install -r ./dev-requirements.txt` or, for just the Ansible runtime requirements, `pip install -r ./requirements.txt`.

#### Modifying the dependency manifest

For best results, a good `requirements.txt` should include the most granular reference possible to a particular version of a package it depends on. `pip-tools` provides the command `pip-compile` to that end, where it takes a generalized list of packages from some input file (`requirements.in`) and it outputs a file that one might have manually completed in `requirements.txt`. Included in the output file are resolved versions of all packages declared in the input file, all underlying dependencies, and each dependency having a version constraint specifying one exact version. Passing the `--generate-hashes` flag to `pip-compile` will take it one step further than version constraints by also including package checksums, verified prior to installing each respective python package.

The output of `pip-compile` is a file that retains full backward-compatibility with `pip install -r`. The benefit is a much smaller, intention-revealing file with only the direct dependencies (`requirements.in`).

To modify the dependencies, modify the input file(s) (`dev-requirements.in` if it's specific to developing ansible code but not needed at runtime, `requirements.in` otherwise) and run `pip-compile --generate-hashes` on the pairings like so:

```
(venv) ~/src/ansible-workspace $ pip-compile --generate-hashes --out-file requirements.in requirements.txt
```

The resulting changes to the input and output files should be tracked in the repository.

#### Ensuring dependencies are tracked

The drawback of using `pip install -r`, despite the output of `pip-compile` being 100% compliant with it, is the case where extra dependencies exist. Say a library used to use a certain python package and now it doesn't. That adds exposure in case there's a CVE published for it, etc. Also, especially with a very fast-growing codebase, how do you know you're not using the orphaned library? This is why installing dependencies from the `requirements.txt` file is recommended through `pip-sync`, another aspect of the `pip-tools` suite.

Running `pip-sync requirements.txt` (or `dev-requirements.txt`) will install all of the dependencies in the requirements file, even going so far as to uninstall any extra python packages you have in the venv that aren't included in it. This makes `pip-sync` more of a blunt object in which to cause pain early on, in case a package you're relying on gets removed unexpectedly, but for greater long-term benefit. The smaller list in the `.in` file becomes easier to curate than the entire snapshot in the `.txt` file.

### Playbooks (`*.yml`)

Ansible playbooks are YAML files that have a specific structure.

```yaml
---

- hosts: botservers
  gather_facts: false
  tasks:
    - name: 'Check if servers are online'
      ping:

```

In the above, exceedingly simple example we see the playbook is a YAML document that is an array of objects. There can be one or more of these objects, but each one must contain the `hosts:` key pointing at a specific host or host group from the inventory (`all` for every one of the hosts from the inventory). In this case, it skips some basic feature detection with the `gather_facts: false` line, and it executes the [`ping` module](https://docs.ansible.com/ansible/latest/modules/ping_module.html) in order to determine if the servers in that host group are online. See the [official Ansible docs](https://docs.ansible.com/ansible/latest/user_guide/playbooks_intro.html) for more.

Our playbooks include the following:

- `get_password_hash.yml` -- A helper for typing in a password locally, when prompted, to have it spit out a well-formed hash for use in creating accounts with the [`user` module](https://docs.ansible.com/ansible/latest/modules/user_module.html)
- `site.yml` -- A build-the-world playbook that provisions the servers from scratch in an idempotent way
- `upgrade_bots.yml` -- A targetted playbook that only upgrades the python bots for TranscribersOfReddit to new versions

### Roles (`roles/*`)

These are a normalized structure for reusable Ansible components, similar to what a "cookbook" is in the Chef config management system.

Technically, everything in a role can be put into one massive playbook, but the approach of using a role allows for more clear intent and organization using the filesystem instead of a YAML structure with lots of scrolling.

For the sake of this monolithic repository, roles are split up in subdirectories like `./roles/{role_name}/`. Each role may contain any or all of these directories (relative to the root of the role):

- `defaults/` -- Default Ansible variables. Variables put in `main.yml` are the lowest precedence items and generally for applying a sane default if no overrides given.
- `handlers/` -- A representation of the `handlers:` section of a playbook, reading `main.yml` within if it exists.
- `meta/` -- A directory that defines metadata about the role, including dependencies on other roles, author information, and supported platforms. All of this is intended to be parsed and acted upon by automation (e.g., platform support).
- `molecule/` -- A directory used for automated testing just this role in isolation with [Molecule](https://molecule.readthedocs.io/en/stable/) and Docker
- `tasks/` -- These are the actual actions taken to provisiona target server, representing the `tasks:` section of a playbook and reading the `main.yml` file implicitly.
- `vars/` -- A list of Ansible variables that may be programmatically included from a task in the role, or for `main.yml` it is automatically included and often is used to override default variable values set in roles this role depends on. Generally it's fine to leave this directory alone.
- `README.md` -- Just the readme outlining the role's purpose, dependencies, and other information for general usage.

More information can be found in [the official ansible documentation on roles](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html).

### Inventory (`inventory/`)

In the context of this monolithic repository, the Ansible inventory is kept as a [submodule](#submodules) pointing to a private repository so that implementation-specific secrets may remain secret for security purposes, yet the majority of the implementation can still adhere to the open source ideals of Grafeas Group.

The function of an Ansible inventory is to provide a manifest of target servers in order to...

- include connection information for each server
- semantically organize each server into one or more groups which can be referenced from a playbook (e.g., `webservers` and `botservers`)
- set server- or group-specific Ansible variable values (i.e., MySQL connection string for `botservers` to use might be different than the one for `webservers` to use)

Since this is a different repository and is subject to change, see the other repository's README for more information on function, directory structure, and overall how to use it.

## Submodules

For this repository we make use of [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules). While it is generally considered an antipattern except in very specific use cases, it proves very useful by keeping certain sections of the code base private in a private repository while the parts that aren't sensitive can remain publicly available.

To clone the repository and all submodules, run `git clone --recursive {clone-url}` instead of just `git clone {clone-url}`. If you're like me, however, you've likely already cloned the repository and need to just pull in the submodule content. Here's how that should go:

```shell
~/src/ansible-workspace $ git submodule init
Submodule 'ansible-secrets' (https://github.com/GrafeasGroup/ansible-secrets) registered for path 'inventory'
~/src/ansible-workspace $ git submodule update
Cloning into 'inventory'...
remote: Enumerating objects: 17, done.
remote: Counting objects: 100% (17/17), done.
remote: Compressing objects: 100% (12/12), done.
remote: Total 17 (delta 0), reused 17 (delta 0), pack-reused 0
Receiving objects: 100% (17/17), 4.89 KiB | 0 bytes/s, done.
Checking connectivity... done.
Submodule path 'inventory': checked out '4e7f0f76fe3393aff5149709bf1dc5b452f6c8ff'
```

Submodules are tracked in the parent repository as a reference to a particular commit, not a rolling pointer to a particular branch. This means they need to be updated from time to time. To do that, all that needs to be done is:

```shell
~/src/ansible-workspace $ cd ./inventory
~/src/ansible-workspace/inventory $ git pull origin master
From https://github.com/GrafeasGroup/ansible-secrets.git
 * branch            master     -> FETCH_HEAD
First, rewinding head to replay your work on top of it...
Fast-forwarded master to bcfdc30e5ed9d863b7374c79cac0aae51d8e4fb8.
~/src/ansible-workspace/inventory $ cd ..
~/src/ansible-workspace $ git add ./inventory
~/src/ansible-workspace $ git commit -m 'Updates submodule reference to latest commit on master branch'
```

[venv]: https://docs.python.org/3/library/venv.html
[pip-tools]: https://molecule.readthedocs.io
[requirements.txt]: https://stackoverflow.com/q/43658870
