# Money Laundering Challenge

This code analyzes bank transaction records in order to detect money laundering activity.  I received the original csv file in a coding challenge as part of one company's job application process.  After finishing the coding challenge, I decided to continue the work on a modified version of the csv file.

Please note that the csv file contains one bank transaction per line.  The transaction includes a transaction Id, date, amount, sender Id, and receiver Id.  Money laundering is suspected when there are two transactions which meet the following conditions:
1. First transaction receiver Id matches the second transaction sender Id
2. Second transaction amount is between 90 and 100% of first transaction amount
3. The two transactions occurred on the same day

## File Contents

1. **money_laundering_challenge.py**: Python code which reads the csv file, splits into groups, then analyzes those groups for money laundering activity
2. **transactions.zip**: Zip file containing a csv file with the bank transaction records

All files shall be downloaded in the same directory.  Please unzip the transactions file before running the program.

## Running the code

This code was written in Python 3 series.  Find the latest Python 3 installation [here](https://www.python.org/downloads/).

Open any Python editor and run **money_laundering_challenge.py**.  Anaconda can be installed from [here](https://www.continuum.io/downloads).  Install for Python 3.X series.