import os
import json
import re
from test import *
from moduleTest import *


def store(file_name, data):
    with open(file_name, 'w') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)


def parse_result_dir(directory, module_test):
    search_depth = 5  # debug
    res = []
    res_json = {'Directory': module_test.directory}
    for test_id in os.listdir(directory):

        """
        Extracting the exception messages from output log files
        """
        output_dir = os.path.join(module_test.directory, "test-runs", "output", test_id)
        exception_dict = {}
        content = open(output_dir, mode='r', encoding='utf-8').readlines()

        rule = "\n([^\t\n]*Exception|[^\t\n]*Error)[^\n]*\n" + "\tat ([^(]+\([^:\)]+:?\d*\))\n" * search_depth
        pattern = re.compile(rule)
        result = pattern.findall(''.join(content))
        for exception_msg in result:
            exception_idx = ''
            for i in range(1, len(exception_msg)):
                res = re.findall(r'.*\((.*)\)', exception_msg[i])[0].split(':')
                exception_idx += res[0] + (res[1] if len(res) > 1 else '')
            exception_dict[exception_idx] = exception_msg[0]

        """
        Extracting test failures from result json files
        """
        test = Test(test_id, module_test)
        test_dir = os.path.join(directory, test_id)
        result_json = []
        with open(test_dir, 'r', encoding='utf8') as fp:
            test.json = json.load(fp)
        test.testOrder = test.json['testOrder']
        test_results = test.json["results"]
        total = 0
        matched = 0
        for key in test_results:
            cur_res = test_results[key]
            if (cur_res['result'] == 'ERROR') | (cur_res['result'] == 'FAIL'):
                stack_trace_raw = ''
                stack_trace = cur_res['stackTrace']
                if stack_trace == []:
                    break
                for i in range(search_depth):
                    line = stack_trace[i]['lineNumber']
                    file = stack_trace[i]['fileName'] if line > 0 else 'Native Method'
                    stack_trace_raw += str(file) + (str(line) if line > 0 else '')

                exception = 'none'
                if stack_trace_raw in exception_dict:
                    exception = exception_dict[stack_trace_raw]
                    matched += 1
                total += 1

                result_json.append(
                    {'Name': cur_res['name'],
                     'Time': cur_res['time'],
                     'Result': cur_res['result'],
                     'Exception': exception,
                     # 'stackTrace': cur_res['stackTrace']
                     })
                test.failures.append(
                    testFailure(cur_res['name'], cur_res['time'], cur_res['result'], cur_res['stackTrace']))

        if test.failures != []:
            res_json[test_id] = result_json

    if len(res_json) > 1:
        store("flaky_lists\\" + test.module_test.moduleName + ".json", res_json)
        print("Success parsing " + test.module_test.moduleName + ", ", matched, "/", total, "matched to exception.")

    return res


def parse_filelist(directory, module_test_list):
    if os.path.isdir(directory):
        for s in os.listdir(directory):
            if s == "test-runs":
                module_name = directory.split('\\')[-1]
                module_test = moduleTest(module_name)
                module_test.directory = directory
                module_test.repository = directory.split('\\')[-3]

                """
                to handle the result json files
                """
                results_dir = os.path.join(directory, s, "results")
                module_test.testSet = parse_result_dir(results_dir, module_test)

                module_test_list.append(module_test)

            else:
                new_dir = os.path.join(directory, s)
                parse_filelist(new_dir, module_test_list)
