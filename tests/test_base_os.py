from .fixtures import elasticsearch


def test_base_os(host):
    assert host.system_info.distribution == 'centos'
    assert host.system_info.release == '7'


def test_no_core_files_exist_in_root(host):
    core_file_check_cmdline = 'ls -l /core*'

    assert host.run(core_file_check_cmdline).exit_status != 0


def test_all_elasticsearch_files_are_gid_0(host):
    check_for_files_with_gid_0_command = (
        "cd /usr/share && "
        "find ./elasticsearch ! -gid 0 | "
        "egrep '.*'"
    )

    assert host.run(check_for_files_with_gid_0_command).exit_status != 0
