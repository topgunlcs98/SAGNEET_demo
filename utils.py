import shutil
import os
import subprocess
import time
import configparser
import json

CONFIG_FILE='/proj/arise/arise/cl4062/CodeEdit/demo/config.ini'
CON = configparser.ConfigParser()
CON.read(CONFIG_FILE, encoding='utf-8')
DATA_CONFIGS = dict(CON.items('D4J'))

D4J_WORKSPACE=DATA_CONFIGS['d4j_workspace']


## insert the patch to its corresponding position
def apply_patch(proj, patch, path, loc):
    bug_path = f'{D4J_WORKSPACE}{proj}/{path}'
    print(bug_path)
    shutil.copyfile(bug_path, bug_path+'.copy')
    with open(bug_path+'.copy', 'r', encoding='utf-8') as f1,\
    open(bug_path, 'w', encoding='utf-8') as f2:
        index = 1
        lines = f1.readlines()
        for line in lines:
            if index == int(loc):
                whitespaces = []
                for i in line:
                    if i == ' ':
                        whitespaces.append(' ')
                    else:
                        break
                f2.write(''.join(whitespaces) + patch + '\n')
            else:
                f2.write(line)
            index += 1


## test the whole project within /timeout
def test_project(proj, timeout=600):
    proj_dir = f'{D4J_WORKSPACE}{proj}'
    os.chdir(proj_dir)
    p = subprocess.Popen(["defects4j", "test", "-r"],stdout=subprocess.PIPE, universal_newlines=True)
    t_beginning = time.time()
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            return 'TIMEOUT'
        time.sleep(1)
    out, err = p.communicate()
    if 'Failing tests: 0' in out:
        return 'Pass'
    else:
        return 'Fail'


## checkout the buggy version of a project
def checkout_d4j_buggy(proj, id):
# defects4j checkout -p Lang -v 1b -w /tmp/lang_1_buggy
    dest_dir = f'{D4J_WORKSPACE}{proj}'
    subprocess.call(["defects4j", "checkout", "-p", proj, "-v", f"{id}b", "-w", dest_dir],shell=False)


## check if the project can be compiled or not
def compile_fix(proj):
    project_dir = f'{D4J_WORKSPACE}{proj}'
    os.chdir(project_dir)
    p = subprocess.Popen(["defects4j", "compile"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if "FAIL" in str(err) or "FAIL" in str(out):
        return False
    return True


def eval_results(path):
    n_match, n_plausible, n_compilable, n_total = 0, 0, 0, 0
    with open(path) as f:
        data = json.load(f)
        for k in data.keys():
            n_total += 1
            if data[k]['status'] == 'Match':
                n_match += 1
                n_plausible += 1
                n_compilable += 1
            elif data[k]['status'] == 'Plausble':
                n_plausible += 1
                n_compilable += 1
            elif data[k]['status'] == 'Compilable':
                n_compilable += 1
    return n_match, n_plausible, n_compilable, n_total


