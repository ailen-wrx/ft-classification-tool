import copy
import json
import re
from test import *
from moduleTest import *
from statMethods import *


def store(file_name, data):
    with open(file_name, 'w') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)

def store1(file_name, data):
    with open(file_name, 'a') as fw:
        json.dump(data, fw, indent=4, ensure_ascii=False)



def parse_result_dir(directory, module_test, flaky_list):
    if module_test.moduleName != "incubator-dubbo-dubbo-common":    # debug
        return
    search_depth = 2                                                # debug
    res_json = {'Directory': module_test.directory}
    flaky_tests = []

    """
    Pre-processing: skipping non-failure test sets
    """

    print("Looking into", module_test.directory, "...", end='')
    for test_id in os.listdir(directory)[:100]:
        test = Test(test_id, module_test)
        try:
            with open(os.path.join(directory, test_id), 'r', encoding='utf8') as fp:
                test.json = json.load(fp)
        except:
            continue
        test_results = test.json["results"]
        for key in test_results:
            if test_results[key]['name'] in flaky_list:
                flaky_tests.append(test_results[key]['name'])
                stack_trace = test_results[key]['stackTrace']
                if not stack_trace:
                    continue
                if len(stack_trace) < search_depth:
                    search_depth = len(stack_trace)

    flaky_tests = list(set(flaky_tests))
    flaky_tests_ = copy.deepcopy(flaky_tests)
    module_test.nFlakies = len(flaky_tests)

    if not flaky_tests:
        print("Skipped.")
        return
    else:
        print("\n[", module_test.moduleName, "]", len(flaky_tests_), "flaky test(s) to find.")

    failures = {}
    multi_mapped_failures = {}
    single_mapped_failures = {}
    print("[", module_test.moduleName, "] Parse begin.")
    for test_id in os.listdir(directory):
        total = 0
        matched = 0
        test = Test(test_id, module_test)
        result_json = []

        """
        Extracting the exception messages from output log files
        """
        output_dir = os.path.join(module_test.directory, "test-runs", "output", test_id)
        exception_dict = {}
        content = open(output_dir, mode='r', encoding='utf-8').readlines()
        rule = "([\w.]+Exception|[\w.]+Error|[\w.]+Failure|[\w.]+Fault)[^\)\w]([^\t]*)" + "\tat ([^\(\n]+\([^:\)\n]+:?\d*\))\n" * search_depth
        pattern = re.compile(rule)
        regex_result = pattern.findall(''.join(content))
        for exception_msg in regex_result:
            exception_idx = ''
            for i in range(2, len(exception_msg)):
                res = re.findall(r'.*\((.*)\)', exception_msg[i])[0].split(':')
                exception_idx += (res[0] + res[1] if len(res) > 1 else 'Unknown') + ', '
            if exception_idx not in exception_dict:
                exception_dict[exception_idx] = []
            exception_msg_dict = {'Name': exception_msg[0], 'Message': exception_msg[1]}
            if exception_msg_dict not in exception_dict[exception_idx]:
                exception_dict[exception_idx].append(exception_msg_dict)

        """
        Matching test failures with exceptions
        """
        try:
            with open(os.path.join(directory, test_id), 'r', encoding='utf8') as fp:
                test.json = json.load(fp)
        except:
            continue
        test_results = test.json["results"]

        for key in test_results:
            if key not in flaky_tests:
                continue
            cur_res = test_results[key]
            if (cur_res['result'] != 'PASS'):
                total += 1
                stack_trace_raw = ''
                stack_trace = cur_res['stackTrace']
                if not stack_trace:
                    continue
                for i in range(search_depth):
                    line = stack_trace[i]['lineNumber']
                    file = stack_trace[i]['fileName'] if line > 0 else 'Unknown'
                    stack_trace_raw += str(file) + (str(line) if line > 0 else '') + ', '

                exception = 'none'
                if stack_trace_raw in exception_dict:
                    exception = exception_dict[stack_trace_raw]
                    if cur_res['name'] not in failures:
                        failures[cur_res['name']] = []
                    if len(exception) > 1:
                        for a in exception:
                            if a not in failures[cur_res['name']]:
                                failures[cur_res['name']].append(a)
                    else:
                        if exception[0] not in failures[cur_res['name']]:
                            failures[cur_res['name']].append(exception[0])
                    matched += 1

                result_json.append(
                    {'Name': cur_res['name'],
                     'Time': cur_res['time'],
                     'Result': cur_res['result'],
                     'Exception': exception,
                     'stackTrace': stack_trace
                     })

                if cur_res['name'] in flaky_tests_:
                    flaky_tests_.remove(cur_res['name'])

        if result_json:
            res_json[test_id] = result_json
            print("[", module_test.moduleName, "]", test_id, ": ", matched, "/", total,
                  "matched to exception, " + str(len(exception_dict)) + " exception(s) detected, "
                  + str(len(flaky_tests_)) + " to find.")

    for key in failures:
        if len(failures[key]) > 1:
            the_types = [a["Name"] for a in failures[key]]
            the_types = list(set(the_types))
            if len(the_types) > 1:
                multi_mapped_failures[key] = failures[key]
            else:
                single_mapped_failures[key] = {'Name': failures[key][0]["Name"], 'Message': failures[key][0]["Message"]}
        else:
            single_mapped_failures[key] = failures[key][0]


    if len(res_json) > 1:
        res_path = os.path.join("flaky_lists", module_test.repository, module_test.moduleName)
        if not os.path.exists(res_path):
            os.makedirs(res_path)
        store(os.path.join(res_path, "all_flaky.json"), res_json)
        if single_mapped_failures:
            print("[", module_test.moduleName, "] Single exception mapped to the stackTrace detected in " +
                  str(len(single_mapped_failures)) + " failure(s).")
            store1(os.path.join(res_path, "single_mapped_failures.json"), single_mapped_failures)
        if multi_mapped_failures:
            print("[", module_test.moduleName, "] Multiple exceptions mapped to the stackTrace detected in " +
                  str(len(multi_mapped_failures)) + " failure(s).")
            store1(os.path.join(res_path, "multi_mapped_failures.json"), multi_mapped_failures)
        print("[", module_test.moduleName, "] " + str(len(flaky_tests_)) + " flaky tests not found.")

        module_test.single_mapped_failures = single_mapped_failures
        module_test.multi_mapped_failures = multi_mapped_failures
        print("[", module_test.moduleName, "] Parse complete.")
        stat_data(module_test)

    return


def parse_filelist(directory, flaky_list):
    if os.path.isdir(directory):
        for s in os.listdir(directory):
            if s == "test-runs":
                module_name = directory.split('\\')[-1]
                module_test = moduleTest(module_name)
                module_test.directory = directory
                module_test.repository = directory.split('\\')[-3]

                results_dir = os.path.join(directory, s, "results")
                if os.path.exists(results_dir):
                    parse_result_dir(results_dir, module_test, flaky_list)

            else:
                new_dir = os.path.join(directory, s)
                parse_filelist(new_dir, flaky_list)
