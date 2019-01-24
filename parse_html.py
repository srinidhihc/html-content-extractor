"""
Title: Program to extract title, and paragraph (if there are more than one paragraph, the contents are delimited by comma) 
from a HTML file.

Author: Srinidhi Havaldar
Company: Alef Education
"""

import os
import pandas as pd
from functools import reduce
from bs4 import BeautifulSoup
from collections import defaultdict


def get_directory_structure(rootdir):
    dir_struct = {}
    rootdir = rootdir.rstrip(os.sep)
    start = rootdir.rfind(os.sep) + 1
    for path, dirs, files in os.walk(rootdir):
        folders = path[start:].split(os.sep)
        subdir = dict.fromkeys(files)
        parent = reduce(dict.get, folders[:-1], dir_struct)
        parent[folders[-1]] = subdir
    return dir_struct


def get_html_path(dict_obj, value, keys=None):
    path = []
    if not keys:
        keys = []
    if value in dict_obj:
        out_keys = keys + [value]
        path.append((out_keys, dict_obj[value]))
    for k, v in dict_obj.items():
        if isinstance(v, dict):
            found_items = get_html_path(v, value, keys=(keys+[k]))
            path = path + found_items
    return path


def get_html_content(html_path):
    math_container = BeautifulSoup(open(html_path), "html.parser")
    title = math_container.find("h3").text.strip()
    paragraph = []
    for tag in math_container.find_all(["p", "li", "span", "td"]):
        p = tag.text.strip()
        paragraph.append(p)
    return title, paragraph


def get_mlo_dict(the_dict, html_filename):
    data_dict = defaultdict(list)
    for each_html in get_html_path(the_dict, html_filename):
        path = each_html[0]
        subject, mlo, lesson, app_dir, html_file = path
        data_dict[mlo].append([lesson, html_file])
    return data_dict


def get_header(html_file):
    soup = BeautifulSoup(open(html_file), "html.parser")
    try:
        title = soup.find("h3").text.strip()
    except:
        title = "NA"
    return title


def get_content(html_file):
    content = []
    soup = BeautifulSoup(open(html_file), "html.parser")
    for tag in soup.find_all(["p", "li", "span", "td"]):
        content.append(tag.text.strip())
    return content

if __name__=='__main__':
    ROOT_DIR = "/Users/s.havaldar/Documents/data/raw_html/MATH-G6"
    math = get_directory_structure(ROOT_DIR)
    mlo_lessons = get_mlo_dict(math, 'index.html')
    df_mlo_lessons = pd.Series(*zip(*((v, k) for k, c in mlo_lessons.items() for v in c))).to_frame('lesson')
    df_mlo_lessons.reset_index(inplace=True)
    df_mlo_lessons[['lessons', 'html_file']] = pd.DataFrame(df_mlo_lessons.lesson.values.tolist())
    df_mlo_lessons.drop('lesson', axis=1, inplace=True)
    df_mlo_lessons = df_mlo_lessons.rename(columns={'index': 'mlo', 'lessons': 'lesson'})
    df_mlo_lessons['subject'] = 'MATH-G6'
    df_mlo_lessons['app_dir'] = 'app'
    df_mlo_lessons['html_path'] = ROOT_DIR + '/' + df_mlo_lessons['mlo'] + '/' + df_mlo_lessons['lesson'] + \
                                  '/' + df_mlo_lessons['app_dir'] + '/' + df_mlo_lessons['html_file']
    df_mlo_lessons['title'] = df_mlo_lessons['html_path'].apply(get_header)
    df_mlo_lessons['content'] = df_mlo_lessons['html_path'].apply(get_content)
