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
    
    return(re.match(b'[0-9a-f]{64}', str.encode(guid)) and \
           re.match(b'[0-9]{4}-[0-9]{2}-[0-9]{2}', str.encode(date)) and \
           re.match(b'[0-9]+\.[0-9]{2}', str.encode(amount)) and \
           re.match(b'ID[0-9]{14}', str.encode(sender)) and \
           re.match(b'ID[0-9]{14}', str.encode(receiver)) and \
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
        
        # This row's items
        amount1 = value_list1[AMOUNT_INDEX]
        sender1 = value_list1[SENDER_INDEX]
        receiver1 = value_list1[RECEIVER_INDEX]
        
        # Loop through the other items
        for key2, value_list2 in trans_dict.items():
            
            # Don't check against itself
            if (key1 == key2):
                continue
        
            # Other row's items
            amount2 = value_list2[AMOUNT_INDEX]
            sender2 = value_list2[SENDER_INDEX]
            receiver2 = value_list2[RECEIVER_INDEX]
            
            # Compare the transactions
            if (receiver1 == sender2 and receiver2 != sender1 and 
                amount2 >= AMOUNT_THRESHOLD*amount1 and amount2 <= amount1):
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

# Check for suspicious transactions
print("Start Dict Processing: ", datetime.now())
keys_set = set()
trans_groups = trans_df.groupby('TimeStamp')
for name, group in trans_groups:
    trans_dict = group.T.to_dict('list')
    keys_set |= get_suspicious_transactions(trans_dict)
print("End Dict Processing: ", datetime.now())

# Select only suspicious transactions
trans_df = trans_df.loc[trans_df.index.isin(keys_set)]

# Suspicoius transactions output file
header = trans_df.columns.values
trans_df.to_csv('suspicious_transactions.csv', columns=header)

# Get counts of IDs and write that to output file
trans_df_counts = trans_df[['Sender', 'Receiver']].apply(pd.Series.value_counts)
trans_df_counts.fillna(0, inplace=True)
trans_df_counts['Total'] = trans_df_counts['Sender'] + trans_df_counts['Receiver']

# Indexing
trans_df_counts.index.names = ['Entity']

# Only need totals in output file
# Note: A middleman will be involved in two transactions
trans_df_counts.drop(['Sender', 'Receiver'], axis=1, inplace=True)
trans_df_counts.sort_values(['Total'], inplace=True, ascending=False)

header = trans_df_counts.columns.values
trans_df_counts.to_csv('suspicious_entities.csv', columns=header)