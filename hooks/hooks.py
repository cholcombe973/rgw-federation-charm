#!/usr/bin/python
#
# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import subprocess
import sys

from charmhelpers.core.hookenv import UnregisteredHookError, Hooks, log, config, \
    ERROR
from charmhelpers.core.host import service_restart
from charmhelpers.fetch import apt_install
import jinja2

hooks = Hooks()

TEMPLATES_DIR = 'templates'


def render_template(template_name, context, template_dir=TEMPLATES_DIR):
    templates = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir))
    template = templates.get_template(template_name)
    return template.render(context)


def generate_region_file():
    region_file_location = os.path.join(os.sep,
                                        'etc',
                                        'ceph',
                                        'region.json')
    context = {
        'name': '',
        'api_name': '',
        'is_master': config('master'),
        'endpoints': [],
        'master_zone': '',
        'zones': [],
        'placement_targets': [],
        'default_placement': '',
    }
    try:
        with open(region_file_location, 'w') as region_file:
            region_file.write(render_template('region.json', context))
    except IOError as err:
        log("IOError writing region.json: {}".format(err), level=ERROR)


def generate_rgw_agent_config_file():
    zone_file_location = os.path.join(os.sep,
                                      'etc',
                                      'ceph',
                                      'radosgw-agent',
                                      'default.conf')
    context = {
        'src_zone': '',
        'source_s3_endpoint': '',
        'main_user_access': '',
        'main_user_secret': '',
        'dest_zone': '',
        'dest_s3_endpoint': '',
        'fallback_user_access': '',
        'fallback_user_secret': '',
        'log_file_location': '',
    }
    try:
        with open(zone_file_location, 'w') as zone_file:
            zone_file.write(render_template('zone.json', context))
    except IOError as err:
        log("IOError writing zone.json: {}".format(err), level=ERROR)
    pass


def generate_zone_file():
    zone_file_location = os.path.join(os.sep,
                                      'etc',
                                      'ceph',
                                      'zone.json')
    context = {
        'domain_root': '',
        'control_pool': '',
        'gc_pool': '',
        'log_pool': '',
        'intent_log_pool': '',
        'usage_log_pool': '',
        'user_keys_pool': '',
        'user_email_pool': '',
        'user_swift_pool': '',
        'user_uid_pool': '',
        'system_key': '',
        'placement_pools': [],
    }
    try:
        with open(zone_file_location, 'w') as zone_file:
            zone_file.write(render_template('zone.json', context))
    except IOError as err:
        log("IOError writing zone.json: {}".format(err), level=ERROR)


def start_agent():
    try:
        service_restart('radosgw-agent')
    except subprocess.CalledProcessError as err:
        log(message='Error: {}'.format(err), level=ERROR)
    pass


@hooks.hook('install')
def install_agent():
    apt_install(['radosgw-agent'])


@hooks.hook('federation.joined')
@hooks.hook('federation.changed')
def federation():
    pass


if __name__ == '__main__':
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))
