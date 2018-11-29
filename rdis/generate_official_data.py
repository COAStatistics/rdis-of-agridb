import linecache as lc
import data_utils
from data_utils import DataGenerator


def load_sample(num) -> None:
    """
    Read sample from txt file then pass line to simple_obj_creator fn
    :param num: 3:main, 4:main_inv, 5:sub, 6:sub_inv
    :return: None
    """

    path = 'info.txt'
    file = lc.getline(path, num).strip()
    with open(file, encoding='utf8') as f:
        for line in enumerate(f):
            ...


if __name__ == '__main__':
    sample_num = eval(input('sample_num = '))
    load_sample(sample_num)
