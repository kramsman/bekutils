""" test upnpacking dictionary like kwargs"""

dic = {'a' : 1, "b": 2}

def unpack_kwarg(*args, **kwargs):
    a = 1

# print(dic)
# print(**dic)
# print(*dic)

unpack_kwarg(**dic)
# unpack_kwarg(a=1, b=2)
a=1
