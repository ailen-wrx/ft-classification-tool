from parseMethods import *
import sys
import json


def store(data):
    with open('flaky_tests.json', 'w') as fw:
        # 将字典转化为字符串
        # json_str = json.dumps(data)
        # fw.write(json_str)
        # 上面两句等同于下面这句
        json.dump(data, fw)


__console = sys.stdout
dataset_path = "..\\dataset\\comprehensive\\12d"

sys.stdout = open("parsing_log", "w")
module_test_list = []
output_json = {}
parse_filelist(dataset_path, module_test_list, output_json)
sys.stdout.close()
sys.stdout = __console
store(output_json)
