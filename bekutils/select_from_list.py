
def select_from_list(lst, box_text='', select_type='check', pre_select=False):
    """ select a list of values from a list using a radio button or check list.
    Clicking 'read' with no selections returns None.

    Args:
        lst (): list of text items to select from
        box_text (): title showing at top of selection
        select_type (): either 'check' for checkbox which allows multi, or 'radio' allows one
        pre_select (): for checkbox whether boxes default to checked (true) or empty (false)
    """

    import PySimpleGUI as sg

    box_title = ''
    font = ("Arial", 15)
    sg.set_options(font=font)

    if select_type == 'check':
        layout = [
            [sg.Text('My layout')],
            [[sg.Checkbox(text, pre_select)] for text in lst],
            [sg.Button('Read')]
        ]
    elif select_type == 'radio':
        layout = [
            [sg.Text(box_text)],
            [[sg.Radio(text, 1)] for text in lst],
            [sg.Button('Read')]
        ]

    window = sg.Window(box_title, layout, )

    while True:  # Event Loop
        event, values = window.Read()
        if event is None:
            break
        # print(event, values)
        if event == "Read" or event == sg.WIN_CLOSED:
            break

    window.close()

    index_values = [key for key, val in values.items() if val]  # index of trues
    index_list = list(values.values())  # values of dict from window, true/falses

    if not index_values:
        return_val = None
    elif select_type == 'radio':
        return_val = lst[index_values[0]]  # take the first (and should be only) element of radio list
    else:
        return_val = [lst[i] for i in range(len(lst)) if index_list[i]]  # list of selected elements

    return return_val


if __name__ == '__main__':

    ll = ['item 1', 'item 2', 'item3', 'item4']
    selected_item = select_from_list(ll, box_text='My BoxText', select_type='check', pre_select=False)
    print(f"{selected_item=}")
    selected_item = select_from_list(ll, box_text='My BoxText', select_type='check', pre_select=True)
    print(f"{selected_item=}")
    selected_item = select_from_list(ll, box_text='My BoxText', select_type='radio', pre_select=False)
    print(f"{selected_item=}")
