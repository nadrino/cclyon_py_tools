


string = "\"0: "

max = 1000
for i in range(max):
    string += "\\uE" + "{:03d}".format(i)
    if (i+1)%30 == 0 and i+1 != max:
        string += "\\n\" \\ \n \"" + str(i + 1) + ": "
    elif (i+1)%10 == 0:
        string += " - "
    else:
        string += " "

print(string)