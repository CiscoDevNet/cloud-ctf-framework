from flask import render_template

from CTFd.utils.logging import log
from CTFd.models import Challenges


class ByoaException(Exception):
    """Exception raised for errors in BYOA "API"

    Attributes:
        http_resp_code -- The http response code to use on the response
        message - The regular message for the exception (for developers, printed to logs)
        user_messages -- list of strings with errors that are safe to print to the end user
    """

    def __init__(self, message, user_messages=None, http_resp_code=500, bcd=None):
        if user_messages is None:
            if http_resp_code == 401:
                user_messages = []
            else:
                user_messages = ["Something unexpected happened"]
        self.http_resp_code = http_resp_code
        self.message = message
        self.user_messages = user_messages
        self.bcd = bcd
        super().__init__(self.message)

    def get_response_from_exception(self):
        # Custom handlers
        log("CiscoCTF", "ByoaException: [{msg}], user_messages: [{user_messages}]", msg=self.message, user_messages=self.user_messages)

        if self.bcd is not None:
            challenge = Challenges.query.filter_by(id=self.bcd.challenge_id).first()
            challenge = challenge.__dict__
            challenge["api_base_uri"] = "i_dont_know_python_imports_are_dumb"
            return render_template("cisco/byoa_challenges/bcd.html", errors=self.user_messages, bcd=self.bcd.__dict__,
                                   challenge=challenge,
                                   banner={"msg": "<br>".join(self.user_messages), "level": "danger"},
                                   metadata=self.bcd.get_byoa_metadata()), self.http_resp_code

        if self.http_resp_code in [400, 401, 409]:
            return render_template(f"cisco/byoa_challenges/{self.http_resp_code}.html", errors=self.user_messages), self.http_resp_code
        # Default to 500 template
        return render_template(f"cisco/byoa_challenges/500.html", errors=self.user_messages), self.http_resp_code
