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
import unittest

from utils.cli_client import CLIClient


class BaseTest(unittest.TestCase):

    def setUp(self):
        super(BaseTest, self).setUp()
        self.created_resources = []
        self.delete_cmd = "{0}"
        self.cli = CLIClient()

    def tearDown(self):
        super(BaseTest, self).tearDown()
        for resource in self.created_resources:
            self.cli.execute_cmd(cmd=self.delete_cmd.format(resource),
                                 fail_ok=True)
