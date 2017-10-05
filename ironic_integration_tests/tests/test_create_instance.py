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
from ironic_integration_tests.common import output_parser as parser


class InstanceTest(BaseTest):

    def setUp(self):
        super(InstanceTest, self).setUp()
        self.delete_cmd = "nova delete {0}"

    def _test_boot_instance(self, image):
        pubkey = self._random_name("testkey_")
        cmd = "ssh-keygen -f /tmp/{0} -N ''".format(pubkey)
        self.cli.execute_cmd(cmd)

        cmd = "nova keypair-add --pub-key /tmp/{0}.pub {0}".format(pubkey)
        self.cli.execute_cmd(cmd)
        self.resource_deletion.append("nova keypair-delete {0}".format(pubkey))

        name = self._random_name("test_boot_instance_")
        cmd = "nova boot --flavor {0} --image {1} --key-name {2} {3}".format(
            "", image, pubkey, name)
        result = self.cli.execute_cmd(cmd)
        server = parser.details(result)
        server_id = server.get("id")
        self.resource_deletion.append("nova delete {0}".format(server_id))

        show_cmd = "nova show {0}".format(server_id)
        server = self.cli.wait_for_status(show_cmd, "status", "ACTIVE")
        self.assertEqual(server.get("status"), "ACTIVE")
        hv_id = server.get("OS-EXT-SRV-ATTR:hypervisor_hostname")
        
        hv_cmd = "nova hypervisor-show {0}".format(hv_id)
        result = self.cli.execute_cmd(hv_cmd)
        hypervisor = parser.details(result)
        self.assertEqual(hypervisor.get("hypervisor_type"), "ironic")

        # ssh into the instance
        # poke around and verify things
        cmd = "nova delete {0}".format(server_id)
        self.cli.execute_cmd(cmd)
        self.cli.wait_for_deletion(show_cmd)

        result = self.cli.execute_cmd(show_cmd, fail_ok=True)
        self.assertIn("No server with a name or ID of", result)

    def test_boot_instance_ubuntu_xenial(self):
        self._test_boot_instance(image="'Ubuntu 16.04 (Xenial)'")
