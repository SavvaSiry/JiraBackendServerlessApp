import json


class AliceRequest(object):
    def __init__(self, request_dict):
        self._request_dict = request_dict

    @property
    def version(self):
        return self._request_dict['version']

    @property
    def session(self):
        return self._request_dict['session']

    @property
    def user_id(self):
        return self.session['user_id']

    @property
    def is_new_session(self):
        return bool(self.session['new'])

    @property
    def command(self):
        return self._request_dict['request']['command']

    def __str__(self):
        return str(self._request_dict)


class AliceResponse(object):
    def __init__(self, alice_request: AliceRequest):
        self._response_dict = {
            "version": alice_request.version,
            "session": alice_request.session,
            "response": {
                "end_session": False
            }
        }

    def dumps(self):
        return json.dumps(
            self._response_dict,
            ensure_ascii=False,
            indent=2
        )

    def set_text(self, text):
        self._response_dict['response']['text'] = text[:1024]

    def set_buttons(self, buttons):
        self._response_dict['response']['buttons'] = buttons

    def end(self):
        self._response_dict["response"]["end_session"] = True

    def __str__(self):
        return self.dumps()


def sent_to_gpt(text):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return 'Sorry, an error occurred while processing your request.'


def process_request(request: AliceRequest) -> AliceResponse:
    response = AliceResponse(request)
    text_in = request.command()
    result = sent_to_gpt(text_in)
    response.set_text(result)
    return response
