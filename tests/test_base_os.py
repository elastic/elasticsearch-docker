def test_base_os(SystemInfo):
    assert SystemInfo.distribution == 'centos'
    assert SystemInfo.release == '7'
