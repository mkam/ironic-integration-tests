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
import random
import string
import unittest
import time

from ironic_integration_tests.common import output_parser as parser
from ironic_integration_tests.common.cli_client import CLIClient, CommandFailed


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.resource_deletion = []
        self.delete_cmd = "{0}"
        self.cli = CLIClient()

    def _random_name(self, prefix, length=5):
        return prefix + "".join(random.sample(string.ascii_letters, length))

    def _create_keypair(self):
        # Create a key pair
        pubkey = self._random_name("testkey_")
        cmd = "ssh-keygen -f /tmp/{0} -N ''".format(pubkey)
        self.cli.execute_cmd(cmd)

        cmd = "nova keypair-add --pub-key /tmp/{0}.pub {0}".format(pubkey)
        self.cli.execute_cmd(cmd)
        self.resource_deletion.append("nova keypair-delete {0}".format(pubkey))
        return pubkey

    def _create_instance(self, image, flavor, pubkey, name):
        cmd = "nova boot --flavor {0} --image '{1}' --key-name {2} {3}".format(
            flavor, image, pubkey, name)
        result = self.cli.execute_cmd(cmd)
        server = parser.details(result)
        server_id = server.get("id")
        self.resource_deletion.append("nova delete {0}".format(server_id))

        # Wait for instance to go to ACTIVE
        show_cmd = "nova show {0}".format(server_id)
        server = self._wait_for_status(show_cmd, "status", "ACTIVE")
        self.assertEqual(server.get("status"), "ACTIVE")
        return server

    def _wait_for_status(self, cmd, status_key, status_value):
        result = self.cli.execute_cmd(cmd)
        resource = parser.details(result)
        attempts = 0
        while resource.get(status_key) != status_value and attempts < 20:
            if resource.get(status_key).lower() == "error":
                return resource
            attempts += 1
            time.sleep(15)
            result = self.cli.execute_cmd(cmd)
            resource = parser.details(result)
        return resource

    def _wait_for_deletion(self, cmd):
        attempts = 0
        try:
            while attempts < 20:
                self.cli.execute_cmd(cmd)
                attempts += 1
                time.sleep(15)
        except CommandFailed:
            return

    def tearDown(self):
        super(BaseTest, self).tearDown()
        for delete_cmd in self.resource_deletion:
            self.cli.execute_cmd(cmd=delete_cmd,
                                 fail_ok=True)
