import os
import json
from test import *
from moduleTest import *


def parse_result_dir(directory, module_test, res_json):
    res = []
    for test_id in os.listdir(directory):
        test = Test(test_id, module_test)
        test_dir = os.path.join(directory, test_id)
        result_json = []
        with open(test_dir, 'r', encoding='utf8') as fp:
            test.json = json.load(fp)
        test.testOrder = test.json['testOrder']
        test_results = test.json["results"]
        for key in test_results:
            cur_res = test_results[key]
            if cur_res['result'] == 'ERROR':
                result_json.append(
                    {'Name': cur_res['name'], 'Time': cur_res['time'], 'stackTrace': cur_res['stackTrace']})
                test.failures.append(testFailure(cur_res['name'], cur_res['time'], cur_res['stackTrace']))

        if (test.failures != []):
            print(test.module_test.repository, " -> ", test.module_test.moduleName, " -> ", test.id, " : [", end='')
            for a in test.failures[:-1]:
                print(a.name, ", ", end='')
            print(test.failures[-1].name, end='')
            print(']')

        if (test.failures != []):
            res_json[test.module_test.repository][test.module_test.moduleName][test_id] = {
                'Directory': test.module_test.directory, 'flakyTests': result_json}

    return res


def parse_filelist(directory, module_test_list, res_json):
    if os.path.isdir(directory):
        for s in os.listdir(directory):
            if s == "test-runs":
                module_name = directory.split('\\')[-1]
                module_test = moduleTest(module_name)
                module_test.directory = directory
                module_test.repository = directory.split('\\')[-3]

                if ~(module_test.repository in res_json):
                    res_json[module_test.repository] = {}
                res_json[module_test.repository][module_name] = {}

                """
                to handle the result json files
                """
                results_dir = os.path.join(directory, s, "results")
                module_test.testSet = parse_result_dir(results_dir, module_test, res_json)

                """
                to handle the output log files
                """
                output_dir = os.path.join(directory, s, "results")

                module_test_list.append(module_test)

            else:
                new_dir = os.path.join(directory, s)
                parse_filelist(new_dir, module_test_list, res_json)
