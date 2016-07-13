import datetime
import math

def currentTerm():
    today = datetime.date.today()
    term = 2 * today.year - 4018
    if today.month < 4:
        term -= 1
    elif today.month > 9:
        term += 1
    return term

def termName(term):
    secondYear = math.ceil((term + 4018) / 2)
    firstYear = secondYear - 1
    name = str(firstYear) + '-' + str(secondYear) + '学年'
    if term % 2:
        name += '第一学期'
    else:
        name += '第二学期'
    return name
