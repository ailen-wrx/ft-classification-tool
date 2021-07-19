import os
import json
from test import *
from moduleTest import *


def parse_result_dir(directory, module):
    res = []
    for test_id in os.listdir(directory):
        test = Test(test_id, module)
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


        # if (test.failures != []):
        #     print(test.module, " : [ ", end='')
        #     for a in test.failures:
        #         print(a.name, ", ", end='')
        #     print(']')


        res.append(test)
    return res

def parse_filelist(dir, module_test_list):
    if os.path.isdir(dir):
        for s in os.listdir(dir):
            if s == "test-runs":
                module_dir = dir.split('\\')[-1]
                module_test = moduleTest(module_dir)
                results_dir = os.path.join(dir, s, "results")
                module_test.testSet = parse_result_dir(results_dir, module_dir)

                module_test_list.append(module_test)
                # print (module_dir, "parse complete")

            else:
                new_dir = os.path.join(dir, s)
                parse_filelist(new_dir, module_test_list)


dataset_path = "..\\dataset\\comprehensive\\12d"

module_test_list = []
parse_filelist(dataset_path, module_test_list)
# print (module_test_list)
