#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 21:12:29 2023

@author: shtk
"""


#%% import data

import myfunctions
import csv
import re
from collections import OrderedDict


path = "Police.csv"
csvfile =  open(path, mode='r', newline='') 
police = csv.reader(csvfile)
header = next(police)

print(header)
print("\n----------------------------------------------------\n")

print('replace date_fk with date_id: ')
myfunctions.replace_value(path, {'date_fk': 'date_id'})

#%%  data understanding

print("\n----------------------------------------------------\n")

# understand data type of each attribute
patterns = {'int': r'^\d+$', 'float':r'^-?\d+\.\d*$', 'non_numeric':r'.*[a-zA-Z].*'}
dtype_name = {}
dtype_ind = {}  
rec_1 = next(police)
for dtype, pattern in patterns.items():
    for i, col in enumerate(rec_1):
        if re.match(pattern, col):
            dtype_ind[i] = dtype
            dtype_name[header[i]] = dtype

# check missing values

missing = ['col_name', 'count_null']
count = [0] * len(header)
for row in police:
    for i, el in enumerate(row):
        if el == '':
            count[i] += 1
if sum(count) == 0:
    print('There is no missing value')


to_print = [['col_index',' col_name', 'count_null', 'dtype']]
to_print[1:] = [ [ind, header[ind], count[ind], dtype_ind[ind] ]for ind in sorted(dtype_ind)]
print('summary of police.csv: ')
myfunctions.print_table(to_print)

#overview of non numeric values

unique = {}
non_numeric = [ key for key, value in dtype_name.items() if value == 'non_numeric']

unique = {}
for attribute in non_numeric:
    values = set(myfunctions.select_attrib(path, [attribute]))
    unique[attribute] = values
    
print('non numeric values: ')
print(unique)
print("\n----------------------------------------------------\n")

# check if all irrelevants correspond to victims
csvfile.seek(0)
next(police)
ind_participant_type, ind_gun_stolen, ind_gun_type = header.index('participant_type'), header.index('gun_stolen'), header.index('gun_type')

count = 0
for i, row in enumerate(police):
    if row[ind_gun_stolen] == 'Irrelevant' :
        if not(row[ind_participant_type] == 'Victim' and row[ind_gun_type] == 'Irrelevant'):
            print(i, row)
            count += 1
if not count:
    print('all irrelevants correspond to victims')
    print("\n----------------------------------------------------\n")

csvfile.close()
       
# count # of unknown gun_type and gun_stolen

gtype = myfunctions.select_attrib(path,['gun_type'])
gstolen =  myfunctions.select_attrib(path,['gun_stolen'])

count = [['type_unknown',myfunctions.count_occurrence(gtype, 'Unknown')],
         ['type_other', myfunctions.count_occurrence(gtype, 'Other')],
         ['stolen_unknown', myfunctions.count_occurrence(gstolen, 'Unknown')]]

to_print = [['col_name', '#_of_meaningless_values']] + count
print('# of meaningless gun_type and gun_stolen values: ')
myfunctions.print_table(to_print)

#%%

print("\n----------------------------------------------------\n")



path_xml = "dates.xml"
path_csv = "dates.csv"
myfunctions.xml_element_to_csv(path_xml, path_csv)

# csv overview
print('xml transferred to csv, a quick overview: ')
data = myfunctions.head(path_csv,3)


# swap 2 cols (to put id in 1st col)
with open(path_csv) as fh:
    reader = csv.reader(fh)
    to_write = []
    for row in reader:
        row[0], row[1] = row[1], row[0]
        to_write.append(row)
    to_write[0][0] = 'date_id' 

# to decide if remove time
all_zero = True
time = '00:00:00"'
for date in to_write[1:]:
    if not date[1].endswith("00:00:00"):
        all_zero = False
        print('Exist different times in the dataset')
        print("\n----------------------------------------------------\n")
        break
if all_zero: 
    print('All times in date col result 00:00:00')
    print("\n----------------------------------------------------\n")
    to_write[1:] = [[date[0], date[1][:-len(time)]] for date in to_write[1:]]

myfunctions.write_csv(path_csv, to_write)

print('remove times from dataset: ')
data = myfunctions.head(path_csv,3)
    

# split and count the date into day, month, year…
with open(path_csv, newline="") as Date:
    reader = csv.reader(Date)
    header = next(reader)
    header += ["day", "month", "year", "quarter", "day_of_the_week"]
    new_rows = [header]

    # get datetime object
    for row in reader:
        detailed = myfunctions.detailed_date(row[1], "%Y-%m-%d")

        new_row = row + detailed
        new_rows.append(new_row)
        
myfunctions.write_csv(path_csv, new_rows)
 
print('dataset with detailed date info: ')       
data = myfunctions.head(path_csv,3)


#%%

# compute crime gravity

names = ['participant_age_group','participant_status','participant_type']
paths_json = ['dict_'+name+'.json' for name in names]
import json
dicts = {}
for path_json in paths_json:
    with open(path_json) as data:
        dic = json.load(data)
        dicts.update(dic)

with open(path) as fh:
    police = fh.readlines()
    row0 = True
    to_write = ['crime_gravity']
    for row in police:
        if row0:
            header = row.strip('\n').split(",")
            inds_to_calculate = []
            for n in names:
                inds_to_calculate += [header.index(n)]
            row0 = False
            continue
        else:
            split_row = row.strip('\n').split(",")
            crime_gravity = 1
            for ind in inds_to_calculate:
                x = split_row[ind]
                crime_gravity *= int(dicts[x])
            to_write.append(str(crime_gravity))

myfunctions.add_col_csv(path, to_write)

#%%

# header of splitted table
participant = ['participant_id', 'participant_age_group', 
               'participant_gender', 'participant_status', 
               'participant_type']
gun = ['gun_id','gun_stolen','gun_type']
geography = ['geo_id','latitude','longitude']
custody = ['custody_id','incident_id', 
           'participant_id','gun_id',""
           'date_id','crime_gravity','geo_id']

tables_name = [participant] + [gun] + [geography] + [custody]
table = dict.fromkeys(['participant','gun','geography', 'custody'])


#%%

# generate missing ids

# participant_id
dicts.update({'Female': 0, 'Male': 1})
dicts['Injured'] = 3
name_id = 'participant_id'

myfunctions.add_id(path, dicts, participant[1:], name_id)


# gun_id
dict_gun = myfunctions.generate_id(unique['gun_type'])
dict_gun_stolen = {'Stolen':1, 'Not-stolen':0}
dict_gun.update(dict_gun_stolen)
name_id = 'gun_id'

myfunctions.add_id(path, dict_gun, gun[1:][::-1], name_id)

# geo_id
unique_coor =  OrderedDict.fromkeys((myfunctions.select_attrib(path, ['latitude', 'longitude'], True)))
dict_geo = myfunctions.generate_id(unique_coor)

with open(path) as f:
    reader = csv.reader(f)
    header = next(reader)
    col_to_write = ['geo_id']
    for row in reader:
        coor = (row[header.index('latitude')],row[header.index('longitude')])
        id = dict_geo[coor]
        col_to_write += [id]
myfunctions.add_col_csv(path, col_to_write)        


#%%

# split original data

header = myfunctions.head(path, 0, False)[0]

for i, key in enumerate(table):
    table[key] = [header.index(name) for name in tables_name[i]]

paths = []
for name in table:
    paths += ["{}.csv".format(name)]

for i, table_name in enumerate(table):
    path_table = paths[paths.index(table_name + ".csv")]
    cols = OrderedDict.fromkeys(myfunctions.select_attrib(path, tables_name[i], True, True)) 
    cols = [list(tup) for tup in cols]
    myfunctions.write_csv(path_table, cols)

csvfile.close()

#%%

# add city, state, country, continent to the geography table 

path_geo = 'geography.csv'
myfunctions.head(path_geo,3)
coordinates = myfunctions.select_attrib(path_geo, ['latitude', 'longitude','geo_id'], True) 

path_cities = "uscities.csv"
myfunctions.head(path_cities,3)
coordinates_map = myfunctions.select_attrib(path_cities, ['lat', 'lng'], True)
city_state_map =  myfunctions.select_attrib(path_cities, ['city', 'state_name'])

header_geo = ['geo_id','city', 'state', 'latitude', 'longitude']
geo_rows = [header_geo]
for coordinate in coordinates:
    map = myfunctions.min_index(coordinate, coordinates_map)
    row = [coordinate[2]] + city_state_map[map] + [coordinate[0]] + [coordinate[1]]
    geo_rows.append(row)

myfunctions.write_csv(path_geo, geo_rows)

path_country = 'city_country_continent.csv'

country_continent = myfunctions.select_attrib(path_country, ['states', 'country', 'continent'])
dict = {}
for el in country_continent:
    if el[0] not in dict:
        dict[el[0]] = el[1:]

with open(path_geo) as geo:
    data = csv.reader(geo)
    header = next(data)
    ind_state = header.index('state') 
    to_write = [['country','continent']]
    for row in data:
        state = row[ind_state]
        to_write += [dict[state]]
myfunctions.add_col_csv(path_geo, to_write)


                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            #%%










