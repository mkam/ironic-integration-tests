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


class InstanceTests(BaseTest):

    def setUp(self):
        super(InstanceTests, self).setUp()
        self.hv_id = None

    def _test_boot_instance(self, image, user):
        # Verify image available
        image_cmd = "glance image-list"
        result = self.cli.execute_cmd(image_cmd)
        images = parser.listing(result)
        image_available = False
        for available_image in images:
            if available_image.get("Name") == image:
                image_available = True
                break
        self.assertTrue(image_available)

        # Create a server
        pubkey = self._create_keypair()
        name = self._random_name("test_boot_instance_")
        server = self._create_instance(
            image=image, flavor="baremetal.general", pubkey=pubkey, name=name)
        server_id = server.get("id")

        # Verify hypervisor type of instance is ironic
        self.hv_id = server.get("OS-EXT-SRV-ATTR:hypervisor_hostname")
        hv_cmd = "nova hypervisor-show {0}".format(self.hv_id)
        result = self.cli.execute_cmd(hv_cmd)
        hypervisor = parser.details(result)
        self.assertEqual(hypervisor.get("hypervisor_type"), "ironic")

        # Verify can ssh into instance
        ssh_address = self._get_ip_address(server)
        ssh_cmd = "ssh -o StrictHostKeyChecking=no -i /tmp/{0} " \
                  "-t {1}@{2} whoami".format(pubkey, user, ssh_address)
        result = self.cli.execute_w_retry(ssh_cmd)
        self.assertIn(user, result)

        # Perform a server action (reboot) works and verify result
        reboot_cmd = "nova reboot {0}".format(server_id)
        self.cli.execute_cmd(reboot_cmd)
        show_cmd = "nova show {0}".format(server_id)
        server = self._wait_for_status(show_cmd, "status", "REBOOT")
        self.assertEqual(server.get("status"), "REBOOT")
        server = self._wait_for_status(show_cmd, "status", "ACTIVE")
        self.assertEqual(server.get("status"), "ACTIVE")
        result = self.cli.execute_w_retry(ssh_cmd)
        self.assertIn("cirros", result)

        # Delete instance and verify deletion
        cmd = "nova delete {0}".format(server_id)
        self.cli.execute_cmd(cmd)
        self._wait_for_deletion(show_cmd)
        result = self.cli.execute_cmd(show_cmd, fail_ok=True)
        self.assertIn("No server with a name or ID of", result)

    def test_boot_instance_ubuntu_xenial(self):
        self._test_boot_instance(image="baremetal-ubuntu-xenial",
                                 user="ubuntu")

    def test_boot_instance_ubuntu_trusty(self):
        self._test_boot_instance(image="baremetal-ubuntu-trusty",
                                 user="ubuntu")

    def test_boot_instance_centos7(self):
        self._test_boot_instance(image="baremetal-centos7-7",
                                 user="centos")

    def tearDown(self):
        super(InstanceTests, self).tearDown()
        if self.hv_id is not None:
            # Wait for ironic node to be cleaned and available
            node_cmd = "ironic node-show {0}".format(self.hv_id)
            self._wait_for_status(node_cmd, "provision_state", "available")
