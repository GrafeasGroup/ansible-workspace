import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_journald_persists_logging(host):
    f = host.file('/var/log/journald')
    journald = host.service('systemd-journald')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'
    assert f.is_dir
    assert journald.is_running
    assert journald.is_enabled


def test_admin_users(host):
    sudoers = host.file('/etc/sudoers.d/sudoers')
    assert sudoers.contains('%sudo ALL=(ALL)')
    assert sudoers.mode == 0o644
