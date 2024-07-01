#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 31 10:50:51 2023

@author: yian
"""

import pandas as pd
import pyodbc

def connect_to_database(server, database, username, password):
    connectionString = (
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
        + server
        + ";DATABASE="
        + database
        + ";UID="
        + username
        + ";PWD="
        + password
    )
    return pyodbc.connect(connectionString)

def create_table(cursor, query):
    cursor.execute(query)

def load_data_from_csv(file_path):
    return pd.read_csv(file_path)

def insert_data(cursor, table_name, df):
    # base on columns of dataframe, create placeholders
    columns = ', '.join(df.columns)
    placeholders = ', '.join('?' * len(df.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    # insert data
    for index, row in df.iterrows():
        cursor.execute(insert_query, tuple(row))
    cursor.connection.commit()

def main():
    # Database Credentials
    server = 'tcp:lds.di.unipi.it'
    database = 'Group_ID_3_DB'
    username = 'Group_ID_3'
    password = 'XHG33RAE'

    # Establishing Connection
    cnxn = connect_to_database(server, database, username, password)
    cursor = cnxn.cursor()

    # CSV file paths
    file_paths = {
        'custody': 'custody.csv',
        'participant': 'participant.csv',
        'gun': 'gun.csv',
        'dates': 'dates.csv',
        'geography': 'geography.csv'
    }

    # Create Tables
    create_table(cursor, '''
    CREATE TABLE [geography](
        [geo_id] INT PRIMARY KEY NOT NULL,
        [latitude] FLOAT,
        [longitude] FLOAT,
        [city] VARCHAR(255),
        [state] VARCHAR(255),
        [continent] VARCHAR(255)
    );

    CREATE TABLE [dates](
        [date_id] INT PRIMARY KEY NOT NULL,
        [date] DATE,
        [day] INT,
        [month] INT,
        [year] INT,
        [quarter] INT,
        [day_of_the_week] VARCHAR(10)
    );

    CREATE TABLE [participant] (
        [participant_id] INT PRIMARY KEY NOT NULL,
        [participant_gender] VARCHAR(10),
        [participant_status] VARCHAR(50),
        [participant_type] VARCHAR(50),
        [participant_age_group] VARCHAR(50)
    );

    CREATE TABLE [gun] (
        [gun_id] INT PRIMARY KEY NOT NULL,
        [gun_stolen] VARCHAR(50),
        [gun_type] VARCHAR(50)
    );

    CREATE TABLE [custody] (
        [custody_id] INT PRIMARY KEY NOT NULL,
        [participant_id] INT,
        [gun_id] INT NOT NULL,
        [geo_id] INT NOT NULL,
        [date_id] INT NOT NULL,
        [incident_id] INT NOT NULL,
        [crime_gravity] INT NOT NULL,
        CONSTRAINT FK_custody_participant FOREIGN KEY (participant_id)
            REFERENCES [participant] (participant_id),
        CONSTRAINT FK_custody_gun FOREIGN KEY (gun_id)
            REFERENCES [gun] (gun_id),
        CONSTRAINT FK_custody_geography FOREIGN KEY (geo_id)
            REFERENCES [geography] (geo_id),
        CONSTRAINT FK_custody_dates FOREIGN KEY (date_id)
            REFERENCES [dates] (date_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
    );
''')


    # Load data and insert into database
    for table, file_path in file_paths.items():
        df = load_data_from_csv(file_path)
        insert_data(cursor, table, df)

    # Closing connection
    cursor.close()
    cnxn.close()

if __name__ == "__main__":
    main()
