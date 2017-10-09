"""
Copyright 2017 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from ironic_integration_tests.tests.base import BaseTest


class VirtIronicTests(BaseTest):

    def setUp(self):
        super(VirtIronicTests, self).setUp()

    def test_mixed_ironic_and_virt_network(self):
        net_name = self._random_name("ironic_virt_")
        net_cmd = "neutron net-create {0}".format(net_name)
        self.cli.execute_cmd(net_cmd)
        subnet_cmd = \
            ("neutron subnet-create --name {0} "
                "--allocation-pool start=192.168.1.1,end=192.168.63.250  "
                "--dns-nameserver=4.4.4.4 {0} 192.168.1.0/18").format(net_name)
        self.cli.execute_cmd(subnet_cmd)
        net_id = ""

        pubkey = self._create_keypair()
        ironic_name = self._random_name("test_network_ironic_")
        ironic_server = self._create_instance(
            image="", flavor="", pubkey=pubkey,
            name=ironic_name, network=net_id)
        ironic_id = ironic_server.get("id")

        virt_name = self._random_name("test_network_virt_")
        virt_server = self._create_instance(
            image="", flavor="", pubkey=pubkey,
            name=ironic_name, network=net_id)
        virt_id = virt_server.get("id")

        ironic_ip = self._get_ip_address(ironic_server)
        virt_ip = self._get_ip_address(virt_server)

        ssh_cmd = "ssh -o StrictHostKeyChecking=no -i /tmp/{0} " \
                  "-t cirros@{1} ping {2} -c 5".format(
                    pubkey, ironic_ip, virt_ip)
        self.cli.execute_w_retry(ssh_cmd)

        ssh_cmd = "ssh -o StrictHostKeyChecking=no -i /tmp/{0} " \
                  "-t cirros@{1} ping {2} -c 5".format(
                    pubkey, virt_ip, ironic_ip)
        self.cli.execute_w_retry(ssh_cmd)
