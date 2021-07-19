from parseMethods import *
import sys

dataset_path = "..\\dataset\\comprehensive\\12d"


sys.stdout = open = open("parsing_log", "w")
module_test_list = []
parse_filelist(dataset_path, module_test_list)

