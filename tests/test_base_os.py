def test_base_os(host):
    assert host.system_info.distribution == 'centos'
    assert host.system_info.release == '7'
