__author__ = 'dy'
import csv
print 'hello'


# append to filename all of the entries in the entry list
def log(filename, entry_list):
    with open(filename, 'ab') as logfile:
        writer = csv.writer(logfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for entry in entry_list:
            writer.writerow(entry)
    return
