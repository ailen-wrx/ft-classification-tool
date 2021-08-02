import os
import csv
import json


def init_flaky():
    res = {}
    with open(os.path.join("pr-data.csv"), 'r') as fr:
        reader = csv.reader(fr)
        for row in reader:
            res[row[3]] = [row[0], row[1], row[2], row[4]]
    return res


def merge(row, dict):
    if row[1] not in dict:
        dict[row[1]] = [row[0], '', row[2], row[3], row[4], row[5]]
    else:
        for i in range(2, 6):
            dict[row[1]][i] = int(dict[row[1]][i]) + int(row[i])


def patch():
    csv.field_size_limit(500 * 1024 * 1024)
    stat_dict = {}
    repo_dict = {}
    result_path = "flaky_lists"
    with open(os.path.join(result_path, "stat.csv"), 'r') as fr:
        reader = csv.reader(fr)
        for row in reader:
            if row[0] == "extended":
                try:
                    with open(os.path.join(result_path, row[0], row[1], "all_flaky.json"), 'r',
                              encoding='utf8') as fp:
                        directory = str(json.load(fp)["Directory"]).split("\\")
                        row[0] = directory[4].rstrip('_output')
                        repo_dict[row[1]] = row[0]
                        merge(row, stat_dict)
                except:
                    continue
            else:
                merge(row, stat_dict)
    with open(os.path.join("stat-flaky-tests.csv"), 'w', newline="") as fw:
        writer = csv.writer(fw)
        for key in stat_dict:
            d = stat_dict[key]
            writer.writerow([d[0], key, d[2], d[3], d[4], d[5]])

    fr = open(os.path.join(result_path, "all_single_mapped_failures.csv"), 'r')
    fw = open(os.path.join("single-mapped.csv"), 'w', newline="")
    reader = csv.reader(fr)
    writer = csv.writer(fw)
    for row in reader:
        if row[0] == "extended":
            if repo_dict[row[1]]:
                row[0] = repo_dict[row[1]]
        writer.writerow(row)
    fr.close()
    fw.close()


def match_flaky():
    csv.field_size_limit(500 * 1024 * 1024)
    exception_dict = {}
    with open(os.path.join("single-mapped.csv"), 'r') as fr:
        reader = csv.reader(fr)
        for row in reader:
            exception_dict[row[2]] = [row[3], row[4]]

    fr = open(os.path.join("pr-data.csv"), 'r')
    fw = open(os.path.join("pr-data-mapped.csv"), 'w', newline="")
    reader = csv.reader(fr)
    writer = csv.writer(fw)
    for row in reader:
        if row[0] == "Project URL":
            nrow = []
            for i in range(5):
                nrow.append(row[i])
            nrow.append('Exception Type')
            nrow.append('Error Messages')
            writer.writerow(nrow)
            continue
        if row[3] in exception_dict:
            msg = exception_dict[row[3]]
            nrow = []
            for i in range(5):
                nrow.append(row[i])
            nrow.append(msg[0])
            nrow.append(msg[1])
            writer.writerow(nrow)
        else:
            nrow = []
            for i in range(5):
                nrow.append(row[i])
            nrow.append('')
            nrow.append('')
            # writer.writerow(nrow)
