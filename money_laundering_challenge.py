# -*- coding: utf-8 -*-
"""
Money Laundering Challenge
William McKee
November 2017
"""

# Initial library declarations
from datetime import datetime
import pandas as pd
import re
import math
from dateutil.parser import parse

GUID_REGEX = b'[0-9a-f]{64}'
DATE_REGEX = b'[0-9]{4}-[0-9]{2}-[0-9]{2}'
AMOUNT_REGEX = b'[0-9]+\.[0-9]{2}'
ENTITY_REGEX = b'ID[0-9]{14}'

def is_date(date_string):
    '''Is the string a proper date?'''
    try:
        parse(date_string)
    except ValueError:
        return False
    return True

def does_item_match_pattern(parts):
    '''Checks to see if a row item matches expected regex pattern'''
    if (len(parts) != 5):
        return False
    
    # Meaningful names
    guid = parts[0].strip()
    date = parts[1].strip()
    amount = parts[2].strip()
    sender = parts[3].strip()
    receiver = parts[4].strip()
    
    return(re.match(GUID_REGEX, str.encode(guid)) and \
           is_date(date) and \
           re.match(AMOUNT_REGEX, str.encode(amount)) and \
           re.match(ENTITY_REGEX, str.encode(sender)) and \
           re.match(ENTITY_REGEX, str.encode(receiver)) and \
           sender != receiver)
    
def parse_row(item):
    '''Parse item and return its parts'''
    parts = item.split('|')
    
    # Item Construction
    item_to_return = []
    if (does_item_match_pattern(parts)):
        for part in parts:
            item_to_return.append(part.strip())
    else:
        for i in range(0,5):
            item_to_return.append('0')
            
    return item_to_return

AMOUNT_INDEX = 1
SENDER_INDEX = 2
RECEIVER_INDEX = 3
AMOUNT_THRESHOLD = 0.9
def get_suspicious_transactions(trans_dict):
    '''
    Return set of indices for suspicious transactions from the transactions dictionary
    trans_dict = dictionary containing key=transactionID and value=list of attributes
    
    Return set of indices for suspicious transactions
    '''
    suspects = set()
    
    # Loop through dictionary
    for key1, value_list1 in trans_dict.items():
        
        # Loop through the other items
        for key2, value_list2 in trans_dict.items():
            
            # Don't check against itself
            if (key1 == key2):
                continue
            
            # Check entity IDs
            receiver1 = value_list1[RECEIVER_INDEX]
            sender2 = value_list2[SENDER_INDEX]
            if (receiver1 == sender2):
                
                # Original receiver not getting money back
                sender1 = value_list1[SENDER_INDEX]
                receiver2 = value_list2[RECEIVER_INDEX]
                if (receiver2 != sender1):
                    
                    # Check the amount exchanged
                    amount1 = value_list1[AMOUNT_INDEX]
                    amount2 = value_list2[AMOUNT_INDEX]
                    if (amount2 >= AMOUNT_THRESHOLD*amount1 and amount2 <= amount1):
                        
                        # Suspicious transaction
                        suspects.add(key1)
                        suspects.add(key2)

    return suspects

print("Start Program: ", datetime.now())

# Read the transactions file
trans_df = pd.read_csv('transactions.csv')

# Data set basic properties
print("Data dimensions: ")
print(trans_df.shape)
print("\n")

print("Column values:")
print(trans_df.columns.values)
print("\n")

# Save column name
col_name = trans_df.columns.values[0]

# Replace single column item with multiple columns
trans_df['Transaction'], trans_df['TimeStamp'], trans_df['Amount'], trans_df['Sender'], trans_df['Receiver'] = \
    zip(*trans_df[col_name].map(parse_row))
trans_df = trans_df.drop(col_name, axis=1)

# Drop rows with invalid information
trans_df = trans_df[trans_df.Transaction != '0']

# Convert column types
trans_df.Amount = trans_df.Amount.astype(float)

# Indexing
trans_df.set_index(('Transaction'), inplace=True)

# Sort by Date
trans_df.sort_values(['TimeStamp'], inplace=True)

# Data set basic properties
print("Data dimensions: ")
print(trans_df.shape)
print("\n")

print("Column values:")
print(trans_df.columns.values)
print("\n")

# Split large data frame into parts
new_df = pd.DataFrame()
trans_groups = trans_df.groupby('TimeStamp')
COUNTER_START_VALUE = 50
number_of_files = math.ceil(len(trans_groups) / COUNTER_START_VALUE)
temp_file_names = []
counter = COUNTER_START_VALUE
file_number = 0

# Write data frame parts to temproary files
for name, group in trans_groups:
    new_df = new_df.append(group)
    if (counter > 0):
        counter -= 1
    else:
        file_name = 't' + str(file_number) + '.csv'
        new_df.to_csv(file_name, columns=trans_df.columns.values)
        new_df = pd.DataFrame()
        temp_file_names.append(file_name)
        counter = COUNTER_START_VALUE
        file_number += 1
        
file_name = 't' + str(file_number) + '.csv'
new_df.to_csv(file_name, columns=trans_df.columns.values)
temp_file_names.append(file_name)
        
print("End DataFrame Processing: ", datetime.now())

# Loop through the temporary files
keys_set = set()
suspect_trans_df = pd.DataFrame(columns=['Transaction', 'TimeStamp', 'Amount', 'Sender', 'Receiver'])
suspect_trans_df.set_index(('Transaction'), inplace=True)
print("Start Dict Processing: ", datetime.now())
for file in temp_file_names:
    print("File ", file)
    trans_df = pd.read_csv(file)
    trans_df.set_index(('Transaction'), inplace=True)
    trans_groups = trans_df.groupby('TimeStamp')

    # Check this dataframe for suspicious transactions
    for name, group in trans_groups:
        trans_dict = group.T.apply(tuple).to_dict()
        keys_set |= get_suspicious_transactions(trans_dict)
    
    # Select only suspicious transactions
    suspect_trans_df = suspect_trans_df.append(trans_df.loc[trans_df.index.isin(keys_set)])
    
print("End Dict Processing: ", datetime.now())

# Suspicoius transactions output file
suspect_trans_df.to_csv('suspicious_transactions.csv', index=['Transaction'],
                        columns=['TimeStamp', 'Amount', 'Sender', 'Receiver'])

# Get counts of IDs and write that to output file
trans_df_counts = suspect_trans_df[['Sender', 'Receiver']].apply(pd.Series.value_counts)
trans_df_counts.fillna(0, inplace=True)
trans_df_counts['Total'] = trans_df_counts['Sender'] + trans_df_counts['Receiver']

# Indexing
trans_df_counts.index.names = ['Entity']

# Only need totals in output file
# Note: A middleman will be involved in two transactions
trans_df_counts.drop(['Sender', 'Receiver'], axis=1, inplace=True)
trans_df_counts.sort_values(['Total'], inplace=True, ascending=False)

trans_df_counts.to_csv('suspicious_entities.csv', columns=trans_df_counts.columns.values)