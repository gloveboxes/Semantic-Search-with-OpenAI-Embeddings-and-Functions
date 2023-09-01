
'''gui to call the OpenAI Whisper Transcribe Server.'''

# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb


import os
import json
import base64
from os import path
import threading
import openai
import PySimpleGUI as sg
import requests

OPENAI_MODEL_NAME = "gpt-3.5-turbo-0613"
OPENAI_MAX_TOKENS = 64
WHISPER_API_KEY_NAME = 'Api-Key'


window = None
bundle_dir = path.abspath(path.dirname(__file__))
e = threading.Event()

get_session = {
    "name": "get_session",
    "description": "Get a session query",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "the session"
            },
            "top_n": {
                "type": "integer",
                "description": "top n sessions"
            }
        },
        "required": ["query"]
    }
}

get_more_sessions = {
    "name": "get_more_sessions",
    "description": "Get more sessions",
    "parameters": {
        "type": "object",
        "properties": {
            "more_sessions": {
                "type": "boolean",
                "description": "get more sessions"
            },
            "number_of_sessions": {
                "type": "integer",
                "description": "the number of sessions to return"
            }
        },
        "required": ["more_sessions"]
    }
}

openai_functions = [
    get_session,
    get_more_sessions
]


def report_more_sessions(function_call, function_arguments):
    '''This function is called when more sessions requested.'''
    print("get more sessions")
    print(function_call)
    print(function_arguments)

    return "return from report sessions", True


def report_sessions(function_call, function_arguments):
    '''This function is called when the assistant is asked for sessions.'''

    top_n = function_arguments.get("top_n", 4)
    top_n = 4 if top_n > 4 else top_n

    search_response = requests.get(
        f"{VECTOR_SEARCH_ENDPOINT}/search?query={function_arguments['query']}&top_n={top_n}", timeout=4)

    if search_response.ok:
        data = search_response.json()

        messages = []
        items = []

        for item in data:
            # get start from item and convert '00:00:01' to seconds
            start = item['start']
            hours, minutes, seconds = start.split(':')
            start_time = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            start_time = str(start_time)

            items.append(
                {"role": "user", "content": f"[{item['title']} by {item['speaker']}](https://www.youtube.com/watch?v={item['videoId']}&t={start_time})"})

            # items.append(
            #     {"role": "user", "content": f"[{item['title']} by {item['speaker']}](https://www.youtube.com/watch?v={item['videoId']}&t={start_time}) and here is a summary: {item['summary']}"})

        # TODO: This needs reviewing as I don't think 100% correct way to do this and causing performance issues

        messages.append({"role": "assistant", "content": None, "function_call": {
                        "name": function_call, "arguments": json.dumps(function_arguments)}})
        messages.append({"role": "function", "name": function_call, "content": json.dumps(items)})

    # Chat History:

    # <|im_start|>user
    # what sessions were on vscode
    # <|im_end|>

        # We call the OpenAI API again, this time providing the assistant with the session details

        response_2 = openai.ChatCompletion.create(
            model=OPENAI_MODEL_NAME,
            messages=messages,
            functions=[get_session]
        )

        return response_2['choices'][0]['message']['content'], True

    return "return from report sessions", True


# these maps are used to make the function name string to the function call
function_map = {"get_session": report_sessions, "get_more_sessions": report_more_sessions}
definition_map = {"get_session": get_session, "get_more_sessions": get_more_sessions}


def get_openai_functions(text, last_assistant_message):
    '''Gets the OpenAI functions from the text.'''

    function_name = None
    arguments = None

    response_1 = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": "You are a system assistant who helps the conference attendees in finding content from past events. Be brief in your answers."},
            {"role": "system", "content": "Answer ONLY with the facts listed in the list of sessions below. If there isn't enough information below, say you don't know. Do not generate answers that don't use the sources below."},
            {"role": "system", "content": "Each source is in the format of a markdown link with the title of the talk and the speaker's name."},
            {"role": "system", "content": "ALWAYS reference source for each fact you use in the response. List each source separately."},
            {"role": "assistant", "content": last_assistant_message},
            {"role": "user", "content": text},
        ],
        functions=openai_functions,
        temperature=0.0,
        max_tokens=OPENAI_MAX_TOKENS
    )

    # The assistant's response includes a function call. We extract the arguments from this function call

    result = response_1.get('choices')[0].get('message')
    content = result.get("content", "")

    if result.get("function_call"):
        function_name = result.get("function_call").get("name")
        arguments = json.loads(result.get("function_call").get("arguments"))

    return content, function_name, arguments


def state_machine():
    '''This is the pipeline thread.'''

    state_counter = 0
    max_loop = 0
    last_assistant_message = ""

    while 1:
        try:

            print("State: ", state_counter)
            # wait for the user to 'send' a query
            if e.is_set():
                max_loop += 1
                # prevent the app from spinning out of control and making too many requests to OpenAI
                if max_loop > 20:
                    e.clear()
                    max_loop = 0
                    state_counter = 0
                    last_assistant_message = ""
                    print("Max conversation length reached. Resetting.")

            e.wait()

            previous_content = window["-CONTENT-"].DefaultText

            # get the function state
            if state_counter == 0:
                query = window["-QUERY-"].get()
                if query == "" and last_assistant_message == "":
                    state_counter = 0
                    continue

                content, function_name, function_arguments = get_openai_functions(
                    query, last_assistant_message)
                if content:
                    last_assistant_message = content
                    print(last_assistant_message)
                    state_counter = 0
                    e.clear()

                    previous_content = content + "\n" + \
                        "--------------------------------------------------" + "\n" + previous_content
                    window.write_event_value("-CONTENT_THREAD-", previous_content)
                    window.refresh()

                elif function_name:
                    state_counter += 1

                    previous_content = "Function name: " + function_name + "\nFunction arguments: " + \
                        json.dumps(function_arguments) + "\n" + \
                        "--------------------------------------------------" + "\n" + previous_content
                    window.write_event_value("-CONTENT_THREAD-", previous_content)
                    window.refresh()

                else:
                    state_counter = 2

            # execute the function state
            elif state_counter == 1:
                content, stop = function_map[function_name](
                    function_name, function_arguments)
                if stop:
                    state_counter = 2
                else:
                    state_counter = 0

                if content is not None:
                    previous_content = content + "\n" + \
                        "--------------------------------------------------" + "\n" + previous_content
                    window.write_event_value("-CONTENT_THREAD-", previous_content)
                    window.refresh()

            # clean up state
            elif state_counter == 2:
                state_counter = 0
                max_loop = 0
                last_assistant_message = ""

                e.clear()

        except Exception as exception:
            print(exception)
            max_loop = 99


def main():
    '''Main function'''
    global window

    button_font = ("Arial", 14)

    user_frame = [
        [
            sg.Button("Send", font=button_font, size=(
                28, 1), key="-SEND-", enable_events=True),
            sg.Input(font=button_font, size=(28, 1),
                     justification="left", expand_x=True, key="-QUERY-"),
        ]
    ]

    conversation_frame = [
        [
            sg.Multiline(key="-CONTENT-", font=("Arial", 18),
                         size=(140, 30), expand_x=True, expand_y=True)
        ],
    ]

    elements = [
        [sg.Frame('Explore', font=button_font, layout=user_frame,
                  expand_x=True, element_justification='center')],
        [sg.Frame('Conversation', font=button_font,
                  layout=conversation_frame, expand_x=True, expand_y=True)],
    ]

    path_to_dat = path.join(bundle_dir, 'icon.png')
    icon_base64 = base64.b64encode(open(path_to_dat, 'rb').read())

    window = sg.Window(title="OpenAI Whisper Audio Transcription",
                       layout=elements, icon=icon_base64,
                       auto_size_text=True, auto_size_buttons=True,
                       resizable=True, finalize=True)

    t = threading.Thread(target=state_machine)
    t.start()

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "-SEND-":
            e.set()

        if event == "-CONTENT_THREAD-":
            window["-CONTENT-"].update(values[event],
                                       text_color="black", background_color="white")

    window.close()


if __name__ == "__main__":

    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    VECTOR_SEARCH_ENDPOINT = os.environ['VECTOR_SEARCH_ENDPOINT']

    openai.api_key = OPENAI_API_KEY

    main()
