""" play with passing optional kws using kwargs"""

def main(df: str, title="DEFAULT TITLE", another_option= "DEFAULT OTHER OPTION", **kwargs):

    print(f"do stuff to df named '{df}' here")
    # do stuff to df here - pass to print and other stuff
    print_df(df, **kwargs)
    another_function(**kwargs)

def print_df(altered_df: str, optional_title= "DEFAULT PRINT TITLE", **kwargs):
    print(f"printing df named '{altered_df}' with title '{optional_title}'")
    another_function(**kwargs)

def another_function(another_option= "DEFAULT OTHER FUNCTION OPTION", **kwargs):
    print(f"use 'another_option' here, set to '{another_option}'")

if __name__ == "__main__":
    # main("my_df", optional_title='custom title', another_option='some other passed option')
    main("my_df", optional_title='custom title', another_option="option from main call")
