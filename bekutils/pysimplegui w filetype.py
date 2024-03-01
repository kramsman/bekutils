""" use pysimplegui to browse files and specify filetype """
import pathlib

from bekutils import exit_yes

## THIS CAN NOT WORK ON MAC VERSIOn Of TKiNTER. https://stackoverflow.com/questions/57443004/pysimplegui-file-browser
# -specific-file-type
## THIS CAN NOT WORK
## THIS CAN NOT WORK

def get_file_name(box_title, title2, initial_dir):
    """ show an "Open" dialog box and return the selected file name. Replaced askopenfilename with pyeasygui
    :param title2: heading of the box
    :type title2: text next to input field
    """

    import PySimpleGUI as sg
    from pathlib import Path
    from loguru import logger

    # layout =  [[sg.In() ,sg.FileBrowse(file_types=(("Text Files", "*.txt"),))]]

    ftype = f"(('Text Files', '*.txt'),)"

    logger.debug('in get_file_name')
    # "Select Sincere address export file 'all-parent-campaign-requests-yyyy-mm-dd.csv'"
    layout = [
        [sg.Text(title2, font=("Arial", 18))],
        [
         sg.Input(key="-IN-", expand_x=True),
         sg.FileBrowse(initial_folder=Path(initial_dir).expanduser(), file_types=(('Text Files', '*.txt'),))
         ],
        [sg.Button("Choose")],
    ]

    # event, values = sg.Window(heading_in_box, layout, size=(600, 100)).read(close=True)
    event, values = sg.Window(box_title, layout, titlebar_font=("Arial", 20), font=("Arial", 14),
                              size=(1000, 150), use_custom_titlebar=True).read(close=True)
    # sg.Window.close()

    file_name = values['-IN-']
    if file_name == "":
        exit_yes("No file name chosen")

    return Path(file_name).expanduser()

if __name__ == '__main__':
    zzz = get_file_name("Get file", "Pick the file you want", pathlib.Path('~/downloads/').expanduser())
    a=1
