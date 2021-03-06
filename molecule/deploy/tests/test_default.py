import os

import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# Define fixture for dynamic ansible role variables.
# @see https://github.com/philpep/testinfra/issues/345#issuecomment-409999558
@pytest.fixture
def ansible_role_vars(host):

    # Include variables from ansible variable files.
    # Paths are relative to the scenario directory.
    ansible_vars = host.ansible(
        "include_vars",
        ("file=../../defaults/main.yml"
         " name=role_defaults"))["ansible_facts"]["role_defaults"]

    ansible_vars.update(host.ansible(
        "include_vars",
        ("file=../../vars/main.yml"
         " name=role_vars"))["ansible_facts"]["role_vars"])

    ansible_vars.update(host.ansible(
        "include_vars",
        ("file=../resources/prepare-vars.yml"
         " name=prepare_vars"))["ansible_facts"]["prepare_vars"])

    ansible_vars.update(host.ansible(
        "include_vars",
        ("file=./scenario-vars.yml"
         " name=scenario_vars"))["ansible_facts"]["scenario_vars"])

    return ansible_vars


def test_index_exists(host, ansible_role_vars):

    f = host.file(ansible_role_vars['wp_install_dir'] + '/index.php')

    assert f.exists


# Functional test for successful deploy.
def test_installed_site_home_page_title(host, ansible_role_vars):

    # Test both that the home page loads at all, and that
    # it contains the configured site title.
    cmd = host.run('curl -s localhost')
    assert '<title>' + ansible_role_vars['wp_site_title'] in cmd.stdout
