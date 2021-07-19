import os
import json
from test import *
from moduleTest import *


def parse_result_dir(directory, module_test):
    res = []
    for test_id in os.listdir(directory):
        test = Test(test_id, module_test)
        test_dir = os.path.join(directory, test_id)
        with open(test_dir, 'r', encoding='utf8') as fp:
            test.json = json.load(fp)
        test.testOrder = test.json['testOrder']
        test_results = test.json["results"]
        for key in test_results:
            cur_res = test_results[key]
            if cur_res['result'] != 'PASS':
                fail = testFailure(cur_res['name'], cur_res['time'], cur_res['stackTrace'])
                test.failures.append(fail)

        if (test.failures != []):
            print(test.module_test.repository, " -> ", test.module_test.moduleName, " -> ", test.id, " : [", end='')
            for a in test.failures[:-1]:
                print(a.name, ", ", end='')
            print(test.failures[-1].name, end='')
            print(']')

        res.append(test)
    return res

def parse_filelist(dir, module_test_list):
    if os.path.isdir(dir):
        for s in os.listdir(dir):
            if s == "test-runs":
                module_name = dir.split('\\')[-1]
                module_test = moduleTest(module_name)
                module_test.directory = dir
                module_test.repository = dir.split('\\')[-3]
                """
                to handle the result json files
                """
                results_dir = os.path.join(dir, s, "results")
                module_test.testSet = parse_result_dir(results_dir, module_test)


                """
                to handle the output log files
                """
                output_dir = os.path.join(dir, s, "results")


                module_test_list.append(module_test)

            else:
                new_dir = os.path.join(dir, s)
                parse_filelist(new_dir, module_test_list)



