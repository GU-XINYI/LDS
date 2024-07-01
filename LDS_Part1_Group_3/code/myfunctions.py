#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 12:38:44 2023

@author: shtk
"""

# xml to csv

def xml_element_to_csv(path_in: str, path_out: str):
    import xml.etree.ElementTree as ET
    tree = ET.parse(path_in)
    root = tree.getroot()

    header = []
    for child in root[0]:
        header += [child.tag]
    
    missing = False
    to_write = [header]  
    for i, child in enumerate(root):
        row = []
        for j, el in enumerate(child):
            if header[j] != root[i][j].tag:
                row += ["?"]
                print('missing value: row {} col {}'.format(i,header[j]))
                missing = True
            else:
                row += [root[i][j].text]
        to_write.append(row)
    if not missing:
        print('There is no missing values in date table')
        print("\n----------------------------------------------------\n")
    else:
        print("\n----------------------------------------------------\n")
    write_csv(path_out, to_write)

            
# get detailed date data

def detailed_date(date: str, format: str):
    from datetime import datetime
    dateStr = date
    datetimeObj = datetime.strptime(dateStr, format)

    day = str(datetimeObj.day)
    month = str(datetimeObj.month)
    year = str(datetimeObj.year)
    quarter = str((datetimeObj.month - 1) // 3 + 1)
    day_of_the_week = datetimeObj.strftime("%A")
    
    return [day, month, year, quarter, day_of_the_week]


# write csv

def write_csv(path: str, to_write):
    with open(path,'w', newline='') as csvfile:
        import csv
        writer = csv.writer(csvfile)
        writer.writerows(to_write)

def add_col_csv(path: str, col_to_write: list):
    with open(path,'r', newline='') as csvfile:
        import csv
        reader = csv.reader(csvfile)
        to_write = []
        for i, row in enumerate(reader):
            if not isinstance(col_to_write[i], list):
                new_row = row + [str(col_to_write[i])]
            else:
                new_row = row + col_to_write[i]
            to_write.append(new_row)
    write_csv(path, to_write)
           
# generate id


def generate_id(data):
    from collections import OrderedDict
    count = 0
    dic =  OrderedDict()
    for el in data:
        count += 1
        dic[el] = count
    return dic


def add_id(path: str, dicts: dict, cols: list, name_id):
    cols_to_use = select_attrib(path, cols)
    ids = [name_id]
    for col in cols_to_use:
        id = ''
        for el in col:
            id += str(dicts.get(el, -1))
        ids += [[id]]
    add_col_csv(path, ids)
               
  


# csv overview

def print_table(data:list):
    from prettytable import PrettyTable
    table = PrettyTable()
    field_names = data[0]
    table.field_names = field_names
    for row in data[1:]:
        table.add_row(row)
    print(table)
    print("\n----------------------------------------------------\n")


def head(path: str, n: int, show = True):
    with open(path,'r', newline='') as csvfile:
        import csv
        reader = csv.reader(csvfile)
        header = next(reader)
        count = 1
        rows = [header]
        for row in reader:
            if count <= n:
                rows.append(row)
                count += 1
            else:
                break
    if show:
        print_table(rows)
    return rows

# select certain attributes
def select_attrib(path: str, attributes, tup = False, include_header = False):
    import csv
    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)
        ind = []
        select = []
        if len(attributes) == 1:
            for row in reader:
                select.append(row[header.index(attributes[0])])
        for attribute in attributes:
            ind += [header.index(attribute)]
        if include_header:
            select = [[header[i] for i in ind]]
        if tup:
            if include_header:
                select[0] = tuple(select[0])
            for row in reader:
                select.append(tuple([row[i] for i in ind]))
        else:
            for row in reader:
                select.append([row[i] for i in ind])
    return select


# count occurrence of a given str

def count_occurrence(l: list, to_count: str):
    from collections import Counter
    counter = Counter(l)
    return counter[to_count]
            
            
# replace certain value

def replace_value(path: str, to_replace:dict):
    with open(path, "r+") as fh:
        content = fh.read()
        for key,value in to_replace.items():
            new_content = content.replace(str(key),str(value))
            print( 'tot # of row (header excluded): {}'.format(content.count('\n')-1))
            print( '{} {} replaced as {}'.format(content.count(key), key, value))
            print("\n----------------------------------------------------\n")
        fh.seek(0)
        fh.truncate()
        fh.write(new_content)

# min distance

def min_index(coordinate1, coordinates):
    import math
    min_distance = float('inf')
    for i,coordinate in enumerate(coordinates):
        distance = math.sqrt((float(coordinate1[0]) - float(coordinate[0]))**2 + (float(coordinate1[1]) - float(coordinate[1]))**2)
        if distance < min_distance:
            min_distance = distance
            min_ind = i
    return min_ind
