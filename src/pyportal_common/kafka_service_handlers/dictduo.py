a = ["kamal", "sai", "apple", "kamal"]
myset = set(a)
mydict = {item: a.count(item) for item in myset}
print(mydict)
