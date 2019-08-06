
"""
Aadam Bari
aadambari@msn.com
05/08/2019

"""

import csv
from decimal import *

def process_sales(path_to_csv):

    sales =	{}

    # open csv file
    with open(path_to_csv) as csv_file:

        # deduce the format of a CSV file and detect whether a header row is present
        has_header = csv.Sniffer().has_header(csv_file.read(1024))
        csv_file.seek(0) #rewind
        data = csv.reader(csv_file)

        #skips header row using next() function
        if has_header:
            next(data)

        # iterate through csv file line by line
        for row in data:
                
            # round time to hour by removing minutes, convert to int
            hour = int(row[1].split(':')[0])

            # print(f'\t{row[0]} was spent at {hour}.')

            # if hour already in dictionary, append transaction value
            # else add the hour and transaction value
            if hour in sales:
                sales[hour] += float(row[0])
                sales[hour] = float(Decimal(sales[hour]).quantize(Decimal('.01'), rounding=ROUND_DOWN)) #round to two decimal places
            else:
                sales[hour] = float(row[0])


        # add hours to dictionary where there were no transactions
        for hour in range(9, 24):
            if hour not in sales:
                # print(hour)
                sales[hour] = 0

        # change hour to %H:%M format
        for hour in range(9, 24):
             sales[str(hour) + ":00"] = sales.pop(hour)

        # print("Sales")
        # print(sales)
        """
        Sales
        {'9:00': 0, '10:00': 130.87, '11:00': 320.64, '12:00': 514.63, '13:00': 406.08, '14:00': 177.77, '15:00': 63.43,
        '16:00': 75.42, '17:00': 142.34, '18:00': 748.62, '19:00': 421.07, '20:00': 0,'21:00': 240.54, '22:00': 0, '23:00': 0}
        """

    return sales


def process_shifts(path_to_csv):

    shifts = {}

    with open(path_to_csv) as csv_file:

        has_header = csv.Sniffer().has_header(csv_file.read(1024))
        csv_file.seek(0) #rewind
        data = csv.reader(csv_file)

        #skips first line of headers
        if has_header:
            next(data)

        for row in data:

            # assign variables for start time hour and finish time hour by spltting csv row and convert to int
            start = int(row[3].split(':')[0])
            finish = int(row[1].split(':')[0])

            # loop to get hours worked
            for hour in range(start, finish + 1):
                # check if hour has ben added to dictionary to add labour cost
                if hour in shifts:
                    shifts[hour] += float(row[2]) #row[2] is payrate
                else:
                    shifts[hour] = float(row[2])

            # function processBreaks takes start tiime of shift, end time of shift and payrate as parameters (extracted from CSV file)
            # returns value of break time
            breaks = processBreaks(row[0].split('-')[0], row[0].split('-')[1], row[2])

            # subtract value of break from sales
            for hour in range(start, finish + 1):
                # If the hours range fall within the hours of the break, subtract payrate for those break hours
                if (breaks['minute'] == 0 and hour >= breaks['start'] and hour < breaks['finish']):
                    shifts[hour] -= breaks['payrate']
                    # Remove cost of break from the hour it falls in (when break time has minutes means it is less than 1 hour)
                elif (breaks['minute'] > 0 and hour == breaks['start']):
                    shifts[hour] -= breaks['cost']

                    
        # change hour to %H:%M format
        for hour in range(9, 24):
            shifts[str(hour) + ":00"] = shifts.pop(hour)     

        # print("Shifts")
        # print(shifts)
        """
        Shifts output
        {'9:00': 30.0, '10:00': 50.0, '11:00': 50.0, '12:00': 64.0, '13:00': 74.0, '14:00': 74.0, '15:00': 44.0, '16:00': 36.67,
         '17:00': 54.0, '18:00': 70.0, '19:00': 66.0, '20:00': 66.0, '21:00': 66.0, '22:00': 66.0, '23:00': 52.0}
        """

    return shifts


def processBreaks(start, finish, payrate):
    """

    :param start:
    :type start: string
    :param finish:
    :type finish: string
    :return: A dictionary with five key-values, 
    employee break start hour (int) with format %H,
    employee break finish hour (int) with format %H, 
    the length of the break in minutes (only calculated if it was less than an hour) (float),
    value of break (float),
    employee payrate (float),

    For example, it should be something like :
    {'start': 15, 'finish': 18, 'minute': 0.0, 'cost': 30.0, 'payrate': 10.0}
    {'start': 18, 'finish': 19, 'minute': 30.0, 'cost': 6.0, 'payrate': 12.0}

    This means the employee started at 3pm, finished at 6pm, they started and finished on the hour, their payrate was 10 so the break was 30 (3 hours labour)

    :rtype: dict
    """

    breakTimes = {}

    # remove PM from time descriptions
    start = start.replace('PM', '')
    finish = finish.replace('PM', '')
    minute = 0
    
    # check if end time of break was not on-the-hour (and thus less than an hour) and extract length of break
    if '.' in finish and '00' not in finish:
        minute = finish.split('.')[1]
    elif '.' in start:
        minute = start.split('.')[1]

    # get cost of break
    # first check if break minutes long or not
    if minute != 0:
        percentage = (int(minute) / 60) * 100
        cost = (float(payrate) / 100) * percentage
    else:
        hours = int(finish) - int(start)
        cost = (float(payrate) * hours)


    # remove minutes for comparison shift hours later on
    start = int(start.split('.')[0])
    finish = int(finish.split('.')[0])
    
    # change to 24 hour clock i.e. 3(pm) becomes 15(:00)
    if finish < 12:
        start += 12
        finish += 12
        
      
    breakTimes['start'] = start
    breakTimes['finish'] = finish
    breakTimes['minute'] = float(minute) 
    breakTimes['cost'] = round(cost, 2)
    breakTimes['payrate'] = float(payrate)

    # print (breakTimes)
    # print(f'\t Break time began at {start} and ended at {finish}, lasted {minute} minutes, payrate is {payrate} so cost is {round(cost, 2)}') 

    return breakTimes

def compute_percentage(shifts, sales):

    profits = {}

    for hour in shifts:
        if sales[hour] != 0:
           percentage = (shifts[hour] / sales[hour] * 100) # percentage of labour cost per sale
           profits[hour] = round(percentage, 2)
        elif sales[hour] == 0:
            profits[hour] = (0 - shifts[hour])

    
    # print("Profits")
    # print(profits)
    """
    Profits
    {'9:00': -30.0, '10:00': 38.21, '11:00': 15.59, '12:00': 12.44, '13:00': 18.22, '14:00': 41.63, '15:00': 69.37, '16:00': 48.62,
    '17:00': 37.94, '18:00': 9.35, '19:00': 15.67, '20:00': -66.0, '21:00': 27.44, '22:00': -66.0, '23:00': -52.0}
    """

    return profits

def best_and_worst_hour(percentages):

    profitable = {}

    # gathers the values greater than 0 (the profitable hours)
    for hour in percentages:
        if percentages[hour] > 0:
            profitable[hour] = percentages[hour]

    # finds best, most profitable hour which is lowet number above zero from percentages (lowest labour cost as percentage of sales)
    highest = min(profitable, key=profitable.get)
    
    
    # finds least profitable hour (hour with greatest cost, highest negative number)
    lowest = min(percentages, key=percentages.get)

    # print(f'\t The best hour was {highest} and the worst hour was {lowest}')

    return (highest, lowest)



def main(path_to_shifts, path_to_sales):
    """
    Do not touch this function, but you can look at it, to have an idea of
    how your data should interact with each other
    """

    shifts_processed = process_shifts(path_to_shifts)
    sales_processed = process_sales(path_to_sales)
    percentages = compute_percentage(shifts_processed, sales_processed)
    best_hour, worst_hour = best_and_worst_hour(percentages)
    return best_hour, worst_hour


# main('work_shifts.csv', 'transactions.csv')
if __name__ == '__main__':
    # You can change this to test your code, it will not be used
    path_to_sales = "transactions.csv"
    path_to_shifts = "work_shifts.csv"
    best_hour, worst_hour = main(path_to_shifts, path_to_sales)


# Aadam Bari