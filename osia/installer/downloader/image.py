from subprocess import Popen, PIPE
from shutil import copyfileobj
from pathlib import Path
from .utils import get_data
import gzip
import requests
import re
import logging
import json

GITHUB_LOCATION="https://raw.githubusercontent.com/openshift/installer/{commit}/data/data/rhcos.json"

def get_commit(installer):
    version_str = ""
    commit_regex = re.compile(r"^.*commit (?P<commit>\w*)$", re.MULTILINE)
    with Popen([installer, "version"], stdout=PIPE, universal_newlines=True) as proc:
        version_str = proc.stdout.read()
    commits = commit_regex.findall(version_str)
    logging.info("Found commits by running installer %s", commits)
    return commits[0]


def get_url(installer):
    commit = get_commit(installer)
    gh_data_link = GITHUB_LOCATION.format(commit=commit)
    rhcos_json = requests.get(gh_data_link, allow_redirects=True)
    rhcos_data = json.loads(rhcos_json.content)
    return rhcos_data['baseURI'] + rhcos_data['images']['openstack']['path'], rhcos_data['buildid']

def _extract_gzip(buff, target):
    result = None
    with gzip.open(buff.name) as zipFile:
        result = Path(target)
        with result.open("wb") as output:
            copyfileobj(zipFile, output)
    return result


def download_image(image_url: str, image_file: str):
    res_file = get_data(image_url, image_file, _extract_gzip)
    return res_file


