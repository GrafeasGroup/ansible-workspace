ToR Bot
=======

Sets up Transcribers of Reddit bots on a server, using systemd and python3

Requirements
------------

- `ansible>=2.9.1,<3`
- `molecule[docker]>=2.22,<3` (optional)

Role Variables
--------------

`archivist_version` -- The version tag on GitHub in which to download tor_archivist

`moderator_version` -- The version tag on GitHub in which to download tor

`ocr_version` -- The version tag on GitHub in which to download tor_ocr

<!--
A description of the settable variables for this role should go here, including
any variables that are in defaults/main.yml, vars/main.yml, and any variables
that can/should be set via parameters to the role. Any variables that are read
from other roles and/or the global scope (ie. hostvars, group vars, etc.) should
be mentioned here as well.
-->

Dependencies
------------

N/a

Example Playbook
----------------

    - hosts: servers
      roles:
         - { role: tor_bot, x: 42 }

License
-------

BSD

Author Information
------------------

- David Alexander <opensource@thelonelyghost.com>
