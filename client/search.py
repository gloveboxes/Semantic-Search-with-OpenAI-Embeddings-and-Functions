'''gui to call the OpenAI Whisper Transcribe Server.'''


import json
import PySimpleGUI as sg
import requests


STOP_RECORDING = False
HOST_ADDRESS = "http://localhost:5500"


def search(query, top_n=10):
    ''' requests get to the search endpoint'''
    endpoint = f"{HOST_ADDRESS}/search"
    result = requests.get(endpoint, timeout=30, params={
                          "query": query, "top_n": top_n})
    if result.status_code == 200:
        # convert the json to a list of dictionaries
        dict_list = json.loads(result.text)
        dict_list = json.loads(dict_list)
        return dict_list
    else:
        return None


def main():
    '''Main function'''

    font = ("Arial", 18)
    button_font = ("Arial", 12)

    # service_config_frame = [
    #     [
    #         sg.Button("Update service config", font=button_font,
    #                   size=(28, 1), key="-UPDATE_CONFIG-"),
    #         sg.Text("Endpoint:", font=font),
    #     ]
    # ]

    query_frame = [
        [
            sg.Button("Search", font=font,
                      size=(20, 1), key="-SEARCH-"),
            sg.Input("solutions architecture", size=(160, 1), key="-QUERY-",
                     font=font, expand_x=True)
        ]
    ]

    # bind a list of dictionaries to the table
    result_frame = [
        [
            sg.Table(
                values=[],
                headings=["Title", "Video Id", "Speaker"],
                col_widths=[40, 20, 20],
                auto_size_columns=False,
                justification="left",
                num_rows=20,
                alternating_row_color="green",
                key="-TABLE-",
                font=font,
                expand_x=True,
                expand_y=True,
                enable_events=True
            ),
            sg.Multiline("", font=font, size=(50, 20),
                         key="-DESCRIPTION-", expand_x=True, expand_y=True)
        ]
    ]

    elements = [
        # [sg.Frame('Whisper service config', font=button_font,
        #           layout=service_config_frame, expand_x=True)],
        [sg.Frame('Search', font=font, vertical_alignment="top",
                  layout=query_frame, expand_x=True)],
        [sg.Frame('Result', font=font, vertical_alignment="top",
                  layout=result_frame, expand_x=True, expand_y=True)],
    ]

    window = sg.Window(title="OpenAI Whisper Audio Transcription",
                       layout=elements,
                       # icon=icon_base64,
                       auto_size_text=True, auto_size_buttons=True,
                       resizable=True, finalize=True)

    while True:
        event, values = window.read()

        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-SEARCH-":
            query = values["-QUERY-"]
            if query == "":
                # sg.popup("Please enter a search query")
                continue

            result = search(query)
            # convert a list of dictionaries to a list of lists
            result_list = [[x["title"], x["videoId"], x["speaker"]]
                           for x in result]

            window['-TABLE-'].update(values=result_list)

            description = result[0]["description"]
            if description is None:
                description = ""

            # replace \n with a space
            description = description.replace("\\n", " ")

            window['-DESCRIPTION-'].update(value=description)

        if event == "-TABLE-":

            row = values.get("-TABLE-")
            if len(row) == 0:
                continue

            # get the selected row
            row = values["-TABLE-"][0]

            description = result[row]["description"]
            if description is None:
                description = ""

            description = description.replace("\\n", " ")

            window['-DESCRIPTION-'].update(value=description)
            # get the title from the first column

            # window['-TABLE-'].update(values=result)

    window.close()


if __name__ == "__main__":

    main()
