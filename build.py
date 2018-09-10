from subprocess import call
import os
import pwd
from pybuilder.core import use_plugin, init, task, depends, description
from pybuilder.errors import BuildFailedException
import zipfile
import shutil
import importlib

use_plugin('python.core')
use_plugin('python.install_dependencies')
use_plugin('python.flake8')
use_plugin('python.pylint')
use_plugin('python.unittest')
use_plugin('python.coverage')
use_plugin('python.integrationtest')

default_task = ['analyze']

dependencies = [
    ('requests', '==2.11.1')
]

user = pwd.getpwuid(os.getuid()).pw_name

@init
def initialize(project):
    project.build_depends_on('boto3', '==1.4.4')
    for name, version in dependencies:
        project.depends_on(name, version)

    project.set_property('dir_dist', '$dir_target/dist/arcane-hacksaw')
    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('coverage_branch_threshold_warn', 90)
    project.set_property('coverage_branch_partial_threshold_warn', 90)
    project.set_property('integrationtest_inherit_environment', True)
    project.set_property('s3_bucket', '.'.join(["test",user]))
    project.set_property('stack_name', ''.join(["DemoStack",user]))


@task
@description('Package the project for deployment')
def package(logger, project):
    for name, _ in dependencies:
        vendor_path = os.path.join('target/dist/arcane-hacksaw', name)
        if os.path.isdir(vendor_path):
            continue
        dep_path = os.path.abspath(os.path.dirname(importlib.import_module(name).__file__))
        shutil.copytree(dep_path, vendor_path)

    with zipfile.ZipFile('target/dist/serverless.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('target/dist/arcane-hacksaw'):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file), 'target/dist/arcane-hacksaw'))
    call_str = 'aws cloudformation package --template-file template.yaml --s3-bucket {bucket} --output-template-file packaged.yaml'.format(bucket=project.get_property("s3_bucket"))
    ret = call(call_str, shell=True)
    if ret != 0:
        logger.error("Error packaging project")
        raise BuildFailedException



@task
@depends('package')
@description('Deploy the project to AWS')
def deploy(logger, project):
    call_str = 'aws cloudformation deploy --template-file packaged.yaml --stack-name {} --capabilities CAPABILITY_IAM'.format(project.get_property("stack_name"))
    ret = call(call_str, shell=True)
    if ret != 0:
        logger.error("Error deploying project to AWS")
        raise BuildFailedException



@task
@description('Removes the project from AWS')
def remove(logger, project):
    call_str = 'aws cloudformation delete-stack --stack-name {}'.format(project.get_property("stack_name"))
    ret = call(call_str, shell=True)
    if ret != 0:
        logger.error('Error removing the deployment from AWS')
        raise BuildFailedException
