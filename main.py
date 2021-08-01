from parseMethods import *
from statMethods import *
from patch import  *

dataset_path = "D:\\iDoFT\\dataset"

stat_init()
list_flaky = init_flaky()
parse_filelist(dataset_path, list_flaky)

patch()
match_flaky()