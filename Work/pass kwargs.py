""" play with passing optional kws using kwargs"""


def main(df, printdf_parms={}, **kwargs):
    print("in main")
    sumdf_parms = kwargs.get('sumdf_parms', {})  # this is awkward to have to set this up

    printdf(df, printdf_parms, **kwargs)

    print("calling printdf but with sumdf_parms")
    printdf(df, sumdf_parms, **kwargs)
    sumdf(df, printdf_parms={'title':'printdf title created in main'}, **kwargs)  # this works but is awkward.
    sumdf(df, tite='printdf title created in main', **kwargs)


def printdf(df, printdf_parms={}, **kwargs):
    title = printdf_parms.get('title', 'printdf Default title')
    print(f"printdf - title: '{title}'")


def sumdf(df, title=None, sumdf_parms={}, **kwargs):
    if title is None:
        title = sumdf_parms.get('title', 'sumdf default title')
    print(f"sumdf - title:'{title}'")


if __name__ == "__main__":
    # below is how to call the functions directly and via main, with different ways of specifying the title

    # uses default
    printdf("mydf")

    # via dedicated dict
    printdf("mydf", printdf_parms={'title': 'printdf title passed directly as "printdf_parm" parameter'})

    # directly via title parameter (which sumdf allows)
    sumdf("mydf", title="sumdf title passed directly as 'title' parameter")

    # passed directly to main via title, picked up by sumdf which allows it.
    main("mydf", title="passed directly to main as title")

    main("mydf",
         printdf_parms={'title': 'printdf title passed to main via dict'},
         sumdf_parms={'title': 'sumdf title passed to main via dict'},
         )
