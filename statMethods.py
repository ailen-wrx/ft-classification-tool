import csv
import os

result_path = "flaky_lists"


def stat_init():
    with open(os.path.join(result_path, "stat.csv"), 'w', newline="") as fw:
        writer = csv.writer(fw)
        writer.writerow(["project", "module", "#total_failures", "#single_mapped", "#multi_mapped", "#none_mapped"])
    with open(os.path.join(result_path, "all_single_mapped_failures.csv"), 'w', newline="") as fw:
        writer = csv.writer(fw)
        writer.writerow(["project", "module", "testName", "exceptionType", "errorMessage"])


def stat_data(module_test):
    mt = module_test
    with open(os.path.join(result_path, "stat.csv"), 'a', newline="") as fw:
        writer = csv.writer(fw)
        nSingle = len(mt.single_mapped_failures)
        nMulti = len(mt.multi_mapped_failures)
        nNone = len(mt.none_mapped_failures)
        writer.writerow([mt.repository, mt.moduleName, nSingle+nMulti+nNone, nSingle, nMulti, nNone])

    with open(os.path.join(result_path, "all_single_mapped_failures.csv"), 'a', newline="") as fw:
        writer = csv.writer(fw)
        json = mt.single_mapped_failures
        for key in json:
            writer.writerow([mt.repository, mt.moduleName, key, json[key][0]["Name"], str(json[key][0]["Message"]).replace('\n', '\\n')])

    return 0
