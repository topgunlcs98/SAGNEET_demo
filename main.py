import configparser
import json
from utils import apply_patch, test_project, checkout_d4j_buggy, compile_fix, eval_results


CONFIG_FILE='/proj/arise/arise/cl4062/CodeEdit/demo/config.ini'
CON = configparser.ConfigParser()
CON.read(CONFIG_FILE, encoding='utf-8')
DATA_CONFIGS = dict(CON.items('DATA'))


def validate_search():
    # search_result_path = DATA_CONFIGS['search_path'] + 'data_retrieved.json'
    '''
    write validation results to /search_result_path
    '''
    search_path = DATA_CONFIGS['root_path'] + 'data_retrieved_test.json'
    search_result_path = DATA_CONFIGS['root_path'] + 'data_retrieved_test_results.json'
    results = {}
    with open(search_path) as f:
        data = json.load(f)
        status = ''
        for k in data.keys():
            bug = k.split('-')[0]
            bug_id = k.split('-')[1]
            start_line = data[k]['location']
            end_line = int(start_line) + 1
            path = data[k]['path']
            patch = data[k]['retreved_patch']
            fix = data[k]['fixes']

            checkout_d4j_buggy(bug, bug_id) ## checkout {bug}-{bug-id}
            apply_patch(bug, patch, path, start_line) ## apply retrieved patch to the buggy project
            
            try:
                res = test_project(bug)
                if res == 'Pass':
                    if fix.replace(' ','') == patch.replace(' ', ''):
                        status = 'Match'
                    else:
                        status = 'Plausable'
                else:
                    res_c =  compile_fix(bug)
                    if res_c:
                        status = 'Compilable'
                    else:
                        status = 'Fail'
            except:
                status = 'Fail'
            res_obj = {
                'path': path,
                'location': start_line,
                'fixes': fix,
                'status': status
            }
            results[k] = res_obj
    with open(search_result_path, 'w', encoding='utf-8') as f1:
        json.dump(results, f1, indent=4)
    print('#'*20)
    print('retrieved patches validated')
    print('#'*20)


def validate_generate():
    '''
    write validation results to /generate_result_path
    '''
    generate_path = DATA_CONFIGS['root_path'] + 'data_generate_test.json'
    generate_result_path = DATA_CONFIGS['root_path'] + 'data_generate_test_results.json'
    results = {}
    with open(generate_path) as f:
            data = json.load(f)
            status = ''
            for k in data.keys():
                bug = k.split('-')[0]
                bug_id = k.split('-')[1]
                start_line = data[k]['location']
                end_line = int(start_line) + 1
                path = data[k]['path']
                patch = data[k]['generated_patch']
                fix = data[k]['fixes']
                status = data[k]['status']
                
                if status == 'Fail' or status == 'Compilable':
                    checkout_d4j_buggy(bug, bug_id)
                    apply_patch(bug, patch, path, start_line)
                    try:
                        res = test_project(bug)
                        if res == 'Pass':
                            if fix.replace(' ','') == patch.replace(' ', ''):
                                status = 'Match'
                            else:
                                status = 'Plausable'
                        else:
                            res_c =  compile_fix(bug)
                            if res_c:
                                status = 'Compilable'
                            else:
                                status = 'Fail'
                    except:
                        status = 'Fail'
                else:
                    ## pass when the bug have been fixed
                    pass
                res_obj = {
                    'path': path,
                    'location': start_line,
                    'fixes': fix,
                    'status': status
                }
                results[k] = res_obj
    with open(generate_result_path, 'w', encoding='utf-8') as f1:
        json.dump(results, f1, indent=4)
    print('#'*20)
    print('generated patches validated')
    print('#'*20)            


def validate_edit():
    '''
    write validation results to /edit_result_path
    '''
    edit_path = DATA_CONFIGS['root_path'] + 'data_edit_test.json'
    edit_result_path = DATA_CONFIGS['root_path'] + 'data_edit_test_results.json'
    results = {}
    with open(edit_path) as f:
            data = json.load(f)
            status = ''
            for k in data.keys():
                bug = k.split('-')[0]
                bug_id = k.split('-')[1]
                start_line = data[k]['location']
                end_line = int(start_line) + 1
                path = data[k]['path']
                patch = data[k]['edited_patch']
                fix = data[k]['fixes']
                status = data[k]['status']
                
                if status == 'Fail' or status == 'Compilable':
                    checkout_d4j_buggy(bug, bug_id)
                    apply_patch(bug, patch, path, start_line)
                    try:
                        res = test_project(bug)
                        if res == 'Pass':
                            if fix.replace(' ','') == patch.replace(' ', ''):
                                status = 'Match'
                            else:
                                status = 'Plausable'
                        else:
                            res_c =  compile_fix(bug)
                            if res_c:
                                status = 'Compilable'
                            else:
                                status = 'Fail'
                    except:
                        status = 'Fail'
                else:
                    ## pass when the bug have been fixed
                    pass
                res_obj = {
                    'path': path,
                    'location': start_line,
                    'fixes': fix,
                    'status': status
                }
                results[k] = res_obj
    with open(edit_result_path, 'w', encoding='utf-8') as f1:
        json.dump(results, f1, indent=4)
    print('#'*20)
    print('edited patches validated')
    print('#'*20) 


def run_all():

    validate_search()
    validate_generate()
    validate_edit()

    retrieved_results_path = DATA_CONFIGS['root_path'] + 'data_retrieved_test_results.json'
    generate_result_path = DATA_CONFIGS['root_path'] + 'data_generate_test_results.json'
    edit_result_path = DATA_CONFIGS['root_path'] + 'data_edit_test_results.json'

    n_match, n_plausible, n_compilable, n_total = eval_results(retrieved_results_path)
    print('#'*10 + 'Patch Search Results' + "#"*10)
    print(f"Total Number:{n_total}")
    print(f"Exact Match:{n_match}")
    print(f"Plausible Patches:{n_plausible}")
    print(f"Compilable Patches:{n_compilable}")

    n_match, n_plausible, n_compilable, n_total = eval_results(generate_result_path)
    print('#'*10 + 'Patch Search + Generate Results' + "#"*10)
    print(f"Total Number:{n_total}")
    print(f"Exact Match:{n_match}")
    print(f"Plausible Patches:{n_plausible}")
    print(f"Compilable Patches:{n_compilable}")

    n_match, n_plausible, n_compilable, n_total = eval_results(edit_result_path)
    print('#'*10 + 'Patch Search + Generate + Edit Results' + "#"*10)
    print(f"Total Number:{n_total}")
    print(f"Exact Match:{n_match}")
    print(f"Plausible Patches:{n_plausible}")
    print(f"Compilable Patches:{n_compilable}")



if __name__ == '__main__':
    run_all()
