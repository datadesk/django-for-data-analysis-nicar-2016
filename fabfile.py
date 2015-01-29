from __future__ import with_statement

import os
import sys
import boto
import time
import random
from fabric.api import *
from os.path import expanduser
from boto.ec2.connection import EC2Connection

pwd = os.path.dirname(__file__)
sys.path.append(pwd)

#
# Production configuration
#

env.key_filename = (expanduser(''),)
env.user = ''
env.known_hosts = ''
env.chef = '/usr/local/bin/chef-solo -c solo.rb -j node.json'
env.app_user = ''
env.project_dir = ''
env.activate = ''
env.branch = 'master'
env.AWS_SECRET_ACCESS_KEY = ''
env.AWS_ACCESS_KEY_ID = ''

def prod():
    """
    The production environment's configuration.
    """
    env.hosts = ("",)

#
# Production operations
#

def create_server(region='us-west-2',
    ami='ami-1cdd532c',
    key_name='ben-datadesk',
    instance_type='m1.medium',
    block_gb_size=12):
    """
    Spin up a new server on Amazon EC2.
    
    Returns the id and public address.
    
    By default, we use Ubuntu 12.04 LTS
    """
    print("Warming up...")
    conn = boto.ec2.connect_to_region(
        region,
        aws_access_key_id = env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key = env.AWS_SECRET_ACCESS_KEY,
    )
    print("Reserving an instance...")
    bdt = boto.ec2.blockdevicemapping.BlockDeviceType(connection=conn)
    bdt.size = block_gb_size
    bdm = boto.ec2.blockdevicemapping.BlockDeviceMapping(connection=conn)
    bdm['/dev/sda1'] = bdt
    reservation = conn.run_instances(
        ami,
        key_name=key_name,
        instance_type=instance_type,
        block_device_map=bdm,
    )
    instance = reservation.instances[0]
    print('Waiting for instance to start...')
    # Check up on its status every so often
    status = instance.update()
    while status == 'pending':
        time.sleep(10)
        status = instance.update()
    if status == 'running':
        print('New instance "' + instance.id + '" accessible at ' + instance.public_dns_name)
    else:
        print('Instance status: ' + status)
    return (instance.id, instance.public_dns_name)


def install_chef():
    """
    Install all the dependencies to run a Chef cookbook
    """
    # Install dependencies
    sudo('apt-get update', pty=True)
    sudo('apt-get install -y git-core rubygems1.9.1 ruby1.9.1 build-essential ruby1.9.1-dev', pty=True)
    # Screw ruby docs.
    sudo("echo 'gem: --no-ri --no-rdoc' > /root/.gemrc")
    sudo("echo 'gem: --no-ri --no-rdoc' > /home/ubuntu/.gemrc")
    # Install Chef
    sudo('gem install --no-ri --no-rdoc chef', pty=True)


def cook():
    """
    Update Chef cookbook and execute it.
    """
    sudo('mkdir -p /etc/chef')
    sudo('chown ubuntu -R /etc/chef')
    local('ssh -i %s -o "StrictHostKeyChecking no" -o "UserKnownHostsFile %s" %s@%s "touch /tmp"' % (
            env.key_filename[0],
            env.known_hosts,
            env.user,
            env.host_string
        )
    )
    local('rsync -e "ssh -i %s -o \'UserKnownHostsFile %s\'" -av ./chef/ %s@%s:/etc/chef' % (
            env.key_filename[0],
            env.known_hosts,
            env.user,
            env.host_string
        )
    )
    sudo('cd /etc/chef && %s' % env.chef, pty=True)


def restart_apache():
    """
    Restarts apache on both app servers.
    """
    sudo("/etc/init.d/apache2 reload", pty=True)


def restart_varnish():
    """
    Restarts apache on both app servers.
    """
    sudo("service varnish restart", pty=True)


def clean():
    """
    Erases pyc files from our app code directory.
    """
    env.shell = "/bin/bash -c"
    with cd(env.project_dir):
        sudo("find . -name '*.pyc' -print0|xargs -0 rm", pty=True)


def install_requirements():
    """
    Install the Python requirements.
    """
    _venv("pip install -r requirements.txt")


def pull():
    """
    Pulls the latest code from github.
    """
    _venv("git pull origin master;")


def syncdb():
    """
    Run python manage.py syncdb over on our prod machine
    """
    _venv("python manage.py syncdb")


def collectstatic():
    """
    Roll out the latest static files
    """
    _venv("rm -rf ./static")
    _venv("python manage.py collectstatic --noinput")


def manage(cmd):
    _venv("python manage.py %s" % cmd)


def _venv(cmd):
    """
    A wrapper for running commands in our prod virturalenv
    """
    with cd(env.project_dir):
        sudo(
            "%s && %s && %s" % (env.activate, env.activate, cmd),
            user=env.app_user
        )


def deploy():
    """
    Deploy the latest code and restart everything.
    """
    pull()
    with settings(warn_only=True):
        clean()
    install_requirements()
    restart_apache()


def load():
    """
    Prints the current load values.
    
    Example usage:
    
        $ fab stage load
        $ fab prod load
        
    """
    def _set_color(load):
        """
        Sets the terminal color for an load average value depending on how 
        high it is.
        
        Accepts a string formatted floating point.

        Returns a formatted string you can print.
        """
        value = float(load)
        template = "\033[1m\x1b[%sm%s\x1b[0m\033[0m"
        if value < 1:
            # Return green
            return template % (32, value)
        elif value < 3:
            # Return yellow
            return template % (33, value)
        else:
            # Return red
            return template % (31, value)
    
    with hide('everything'):
        # Fetch the data
        uptime = run("uptime")
        # Whittle it down to only the load averages
        load = uptime.split(":")[-1]
        # Split up the load averages and apply a color code to each depending
        # on how high it is.
        one, five, fifteen = [_set_color(i.strip()) for i in load.split(',')]
        # Get the name of the host that is currently being tested
        host = env['host']
        # Combine the two things and print out the results
        output = u'%s: %s' % (host, ", ".join([one, five, fifteen]))
        print(output)


def ps(process='all'):
    """
    Reports a snapshot of the current processes.

    If the process kwarg provided is 'all', every current process is returned.

    Otherwise, the list will be limited to only those processes that match the kwarg.

    Example usage:

        $ fab prod ps:process=all
        $ fab prod ps:process=httpd
        $ fab prod ps:process=postgres

    Documentation::

        "ps":http://unixhelp.ed.ac.uk/CGI/man-cgi?ps

    """
    if process == 'all':
        run("ps aux")
    else:
        run("ps -e -O rss,pcpu | grep %s" % process)

def ssh():
    local("ssh ubuntu@%s -i %s" % (env.hosts[0], env.key_filename[0]))

#
# Local operations
#


def update_templates(template_path='./templates'):
    """
    Download the latest template release and load it into your system.
    
    It will unzip to "./templates" where you run it.
    """
    with lcd(template_path):
        local("curl -O http://databank-cookbook.latimes.com/dist/templates/latest.zip")
        local("unzip -o latest.zip")
        local("rm latest.zip")


def generate_secret(length=50,
    allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'):
    """
    Generates secret key for use in Django settings.
    """
    key = ''.join(random.choice(allowed_chars) for i in range(length))
    print 'SECRET_KEY = "%s"' % key


def rmpyc():
    """
    Erases pyc files from current directory.

    Example usage:

        $ fab rmpyc

    """
    print("Removing .pyc files")
    with hide('everything'):
        local("find . -name '*.pyc' -print0|xargs -0 rm", capture=False)


def rs(port=8000):
    """
    Fire up the Django test server, after cleaning out any .pyc files.

    Example usage:
    
        $ fab rs
        $ fab rs:port=9000
    
    """
    with settings(warn_only=True):
        rmpyc()
    local("python manage.py runserver 0.0.0.0:%s" % port, capture=False)


def sh():
    """
    Fire up the Django shell, after cleaning out any .pyc files.

    Example usage:
    
        $ fab sh
    
    """
    rmpyc()
    local("python manage.py shell", capture=False)


def tabnanny():
    """
    Checks whether any of your files have improper tabs
    
    Example usage:
    
        $ fab tabnanny
    
    """
    print("Running tabnanny")
    with hide('everything'):
        local("python -m tabnanny ./")


def pep8():
    """
    Flags any violations of the Python style guide.

    Requires that you have the pep8 package installed

    Example usage:

        $ fab pep8

    Documentation:

        http://github.com/jcrocholl/pep8

    """
    print("Checking Python style")
    # Grab everything public folder inside the current directory
    dir_list = [x[0] for x in os.walk('./') if not x[0].startswith('./.')]
    # Loop through them all and run pep8
    results = []
    with hide('everything'):
        for d in dir_list:
            results.append(local("pep8 %s" % d))
    # Filter out the empty results and print the real stuff
    results = [e for e in results if e]
    for e in results:
        print(e)


def big_files(min_size='20000k'):
    """
    List all files in this directory over the provided size, 20MB by default.
    
    Example usage:
    
        $ fab big_files
    
    """
    with hide('everything'):
        list_ = local("""find ./ -type f -size +%s -exec ls -lh {} \; | awk '{ print $NF ": " $5 }'""" % min_size)
    if list_:
        print("Files over %s" % min_size)
        print(list_)
    else:
        print("No files over %s" % min_size)
