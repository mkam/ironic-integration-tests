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

from ironic_integration_tests.common.cli_client import CLIClient


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.resource_deletion = []
        self.delete_cmd = "{0}"
        self.cli = CLIClient()

    def _random_name(self, prefix, length=5):
        return prefix + "".join(random.sample(string.ascii_letters, length))

    def tearDown(self):
        super(BaseTest, self).tearDown()
        for delete_cmd in self.resource_deletion:
            self.cli.execute_cmd(cmd=delete_cmd,
                                 fail_ok=True)
