__author__ = 'dy'
# import csv
import unicodecsv


# def log(filename, entry_list):
#     with open(filename, 'ab') as logfile:
#         writer = csv.writer(logfile, delimiter=' ',
#                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
#         for entry in entry_list:
#             writer.writerow(entry)
#     return

# append to filename all of the entries in the entry list
# updated to work with unicode, hopefully
def log(filename, entry_list):
    with open(filename, 'ab') as logfile:
        writer = unicodecsv.writer(logfile, encoding='utf-8')
        for entry in entry_list:
            writer.writerow(entry)
    return

def unitest():
    unilog('unitest.csv', [[u'\u304f', u'\u304f']])
    with open('unitest.csv', 'r') as f:
        r = unicodecsv.reader(f, encoding='utf-8')
        row = r.next()
        print 'row[0] = ', row[0], 'row[1] = ', row[1]

# unitest()