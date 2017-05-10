from .fixtures import elasticsearch


def test_base_os(host):
    assert host.system_info.distribution == 'centos'
    assert host.system_info.release == '7'


def test_java_home_env_var(host):
    java_path_cmdline = '$JAVA_HOME/bin/java -version'

    assert host.run(java_path_cmdline).exit_status == 0
