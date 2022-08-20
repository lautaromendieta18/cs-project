
def hora(value):
    return value.strftime("%H:%M")

def fecha(value):
    return "%s-%s-%s" % (value.day, value.month, value.year)