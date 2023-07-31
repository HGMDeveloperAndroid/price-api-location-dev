# -*- coding: utf-8 -*-
from fabric.api import env, require, run, task
from fabric.colors import green, white
from fabric.utils import puts

from fabutils.context import cmd_msg
from fabutils.env import set_env_from_json_file
from fabutils.tasks import ulocal, ursync_project
from fabutils.text import SUCCESS_ART


env.shell = "/bin/zsh -l -c"


@task
def environment(env_name):
    """Creates environment.

    Creates a dynamic environment based on the contents of the given
    environments_file.

    Args:
        env_name(str): Name environment.
    """
    if env_name == 'vagrant':
        result = ulocal('vagrant ssh-config | grep IdentityFile', capture=True)
        env.key_filename = result.split()[1].replace('"', '')

    set_env_from_json_file('environments.json', env_name)


@task
def deploy(git_ref, upgrade=False):
    """Deploy project.

    Deploy the code of the given git reference to the previously selected
    environment.

    Args:
        upgrade(Optional[bool]):
            Pass ``upgrade=True`` to upgrade the versions of the already
            installed project requirements (with pip)
        git_ref(str): name branch you make deploy.

    Example:
        >>>fab environment:vagrant deploy:devel.
    """
    require('hosts', 'user', 'group', 'site_dir')

    # Retrives git reference metadata and creates a temp directory with the
    # contents resulting of applying a ``git archive`` command.
    message = white('Creating git archive from {0}'.format(git_ref), bold=True)
    with cmd_msg(message):
        repo = ulocal(
            'basename `git rev-parse --show-toplevel`', capture=True)
        commit = ulocal(
            'git rev-parse --short {0}'.format(git_ref), capture=True)
        branch = ulocal(
            'git rev-parse --abbrev-ref HEAD', capture=True)

        tmp_dir = '/tmp/blob-{0}-{1}/'.format(repo, commit)

        ulocal('rm -fr {0}'.format(tmp_dir))
        ulocal('mkdir {0}'.format(tmp_dir))
        ulocal('git archive {0} ./app | tar -xC {1} --strip 1'.format(
            commit, tmp_dir))

    # Uploads the code of the temp directory to the host with rsync telling
    # that it must delete old files in the server, upload deltas by checking
    # file checksums recursivelly in a zipped way; changing the file
    # permissions to allow read, write and execution to the owner, read and
    # execution to the group and no permissions for any other user.
    with cmd_msg(white('Uploading code to server...', bold=True)):
        ursync_project(
            local_dir=tmp_dir,
            remote_dir=env.site_dir + '/app',
            delete=True,
            default_opts='-chrtvzP',
            extra_opts='--chmod=750',
            exclude=["*.pyc", "env/", "cover/"]
        )

    # Performs the deployment task, i.e. Install/upgrade project
    # requirements, syncronize and migrate the database changes, collect
    # static files, reload the webserver, etc.
    message = white('Running deployment tasks', bold=True)
    with cmd_msg(message, grouped=True):
        message = white('Installing Python requirements with pip')
        with cmd_msg(message, spaces=2):
            run('pip install -{0}r {1}/app/requirements.txt'.format(
                'U' if upgrade else '', env.site_dir
            ))

        message = white('Setting file permissions')
        with cmd_msg(message, spaces=2):
            run('chgrp -R {0} .'.format(env.group))

        message = white('Restarting webserver')
        with cmd_msg(message, spaces=2):
            run('sudo supervisorctl restart {}-gunicorn'.format(env.user))

    # Clean the temporary snapshot files that was just deployed to the host
    message = white('Cleaning up...', bold=True)
    with cmd_msg(message):
        ulocal('rm -fr {0}'.format(tmp_dir))

    puts(green(SUCCESS_ART), show_prefix=False)
    puts(white('Code from {0} was succesfully deployed to host {1}'.format(
        git_ref, ', '.join(env.hosts)), bold=True), show_prefix=False)
