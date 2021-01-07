Reddit Bots
===========

Setup process for Python-based Reddit bots in general

Requirements
------------

_N/a_

Role Variables
--------------

**Required:**

- `bot` (`dict`):
  - `bot.username` (`str`): Reddit username
  - `bot.password` (`str`): Reddit password
  - `bot.client_id` (`str`): OAuth public key
  - `bot.client_secret` (`str`): OAuth secret key
- `bot_name` (`str`): Internal representation for this specific bot. This will be the systemd service name and a pivot point for how all configuration will be named.
- `bot_repo` (`str`): From GitHub, this is the `fizzbuzz` part of `https://github.com/GrafeasGroup/fizzbuzz`
- `bot_cmd` (`str`): The name of the command invoked to run the bot, as noted in `console_scripts` in `setup.py` (or equivalent in `pyproject.toml`)

**Optional:**

- `venv_path` (`str`): Absolute path on the target VM where the virtualenv will be hosted. Defaults to a directory named `venv/` in the bot user's home directory
- `user_home` (`str`): Absolute path on the target VM to where the bot's local user account will have its `$HOME` set. Defaults to `/home/{{ bot_name }}`
- `python_bin` (`str`): Absolute path to a python3 binary to use for python-related actions. Defaults to `/usr/local/bin/python3`
- `env` (`dict`): A map of variable names to associated values that should be set in the bot's runtime environment. Each key should follow posix shell requirements for `export {var_name}={var_value}` type of syntax. Default is an empty map

Dependencies
------------

_N/a_

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: bots
      tasks:
        - import_role: reddit_bot
          vars:
            env:
              NOOP: 1
            bot_repo: github-repo-name
            bot_name: shortname-goes-here
            bot_cmd: bot-command

License
-------

MIT

Author Information
------------------

- David Alexander (@TheLonelyGhost, <https://www.thelonelyghost.com/>)
