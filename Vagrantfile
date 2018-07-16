# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure('2') do |config|
  config.vm.box = 'bento/ubuntu-18.04'

  config.vm.provider 'virtualbox' do |vb|
    vb.memory = '4096'
  end

  config.vm.synced_folder '.', '/vagrant', owner: 'vagrant', group: 'root'

  config.vm.provision 'shell', inline: <<-SHELL
    apt-get update
    apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      python3-pip \
      software-properties-common
    pip3 install virtualenv
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    apt-get update
    apt-get install -y docker-ce
    usermod --groups docker --append vagrant

    echo vm.max_map_count=262144 > /etc/sysctl.d/vm_max_map_count.conf
    sysctl --system

    grep -qF 'vagrant - nofile 65536' /etc/security/limits.conf || echo 'vagrant - nofile 65536' >> /etc/security/limits.conf
  SHELL

end
