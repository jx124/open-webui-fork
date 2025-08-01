from enum import Enum


class MESSAGES(str, Enum):
    DEFAULT = lambda msg="": f"{msg if msg else ''}"
    MODEL_ADDED = lambda model="": f"The model '{model}' has been added successfully."
    MODEL_DELETED = (
        lambda model="": f"The model '{model}' has been deleted successfully."
    )


class WEBHOOK_MESSAGES(str, Enum):
    DEFAULT = lambda msg="": f"{msg if msg else ''}"
    USER_SIGNUP = lambda username="": (
        f"New user signed up: {username}" if username else "New user signed up"
    )


class ERROR_MESSAGES(str, Enum):
    def __str__(self) -> str:
        return super().__str__()

    DEFAULT = lambda err="": f"Something went wrong :/\n{err if err else ''}"
    ENV_VAR_NOT_FOUND = "Required environment variable not found. Terminating now."
    CREATE_USER_ERROR = "Oops! Something went wrong while creating your account. Please try again later. If the issue persists, contact support for assistance."
    DELETE_USER_ERROR = "Oops! Something went wrong. We encountered an issue while trying to delete the user. Please give it another shot."
    EMAIL_MISMATCH = "This email does not match the email your provider is registered with. Please check your email and try again."
    EMAIL_TAKEN = "This email is already registered. Sign in with your existing account or choose another email to start anew."
    USERNAME_TAKEN = (
        "This username is already registered. Please choose another username."
    )
    COMMAND_TAKEN = lambda cmd="": f"The command {cmd} is already registered. Please choose another command string."
    CLASS_NAME_TAKEN = lambda cmd="": f"The class name {cmd} is already registered. Please choose another name."
    FILE_EXISTS = "This file is already registered. Please choose another file."

    MODEL_ID_TAKEN = "This model id is already registered. Please choose another model id string."

    NAME_TAG_TAKEN = "This name tag is already registered. Please choose another name tag string."
    ROLE_NAME_TAKEN = lambda name="": f"The role name {name} is already registered. Please choose another role name string."
    INVALID_TOKEN = (
        "Your session has expired or the token is invalid. Please sign in again."
    )
    INVALID_CRED = "The email or password provided is incorrect. Please check for typos and try logging in again."
    INVALID_EMAIL_FORMAT = lambda email="": f"The email format you entered is invalid{(': ' + email) if email else ''}. Please double-check and make sure you're using a valid email address (e.g., yourname@example.com)."
    INVALID_PASSWORD = (
        "The password provided is incorrect. Please check for typos and try again."
    )
    INVALID_TRUSTED_HEADER = "Your provider has not provided a trusted header. Please contact your administrator for assistance."
    INVALID_ROLE_CHANGE = "You are not allowed to change the 'pending', 'admin', or 'instructor' roles."
    INVALID_ROLE_FORMAT = "Role names cannot contain commas and must be at most 255 characters long."
    INVALID_ROLE_DELETION = lambda num=0: f"This role cannot be deleted as {num} {'user is' if num==1 else 'users are'} assigned to it."
    DUPLICATE_ROLES = "Roles must be unique."
    EXISTING_USERS = "You can't turn off authentication because there are existing users. If you want to disable WEBUI_AUTH, make sure your web interface doesn't have any existing users and is a fresh installation."
    INVALID_DURATION = "Invalid duration format."

    UNAUTHORIZED = "401 Unauthorized"
    ACCESS_PROHIBITED = "You do not have permission to access this resource. Please contact your administrator for assistance."
    ACTION_PROHIBITED = (
        "The requested action has been restricted as a security measure."
    )

    FILE_NOT_SENT = "FILE_NOT_SENT"
    FILE_NOT_SUPPORTED = "Oops! It seems like the file format you're trying to upload is not supported. Please upload a file with a supported format (e.g., JPG, PNG, PDF, TXT) and try again."

    INVALID_IMPORT_FILE = "The file cannot be opened."
    INVALID_EMAILS = "There are repeated emails or emails that are already taken."
    MISSING_COLUMNS_IMPORT = lambda cols: f"Missing columns: {', '.join(cols)}"
    MISSING_ROLES = lambda roles: f"These roles do not exist: {', '.join(roles)}. Please create the roles before importing new users."
    MISSING_EMAILS = lambda emails: f"These emails do not exist: {', '.join(emails)}. Please import these users first via Admin Panel > Add Users."
    EXISTING_EMAIL_IMPORT = lambda emails: f"These emails are already in use: {', '.join(emails)}"

    NOT_FOUND = "We could not find what you're looking for :/"
    USER_NOT_FOUND = "We could not find what you're looking for :/"
    API_KEY_NOT_FOUND = "Oops! It looks like there's a hiccup. The API key is missing. Please make sure to provide a valid API key to access this feature."

    MALICIOUS = "Unusual activities detected, please try again in a few minutes."

    PANDOC_NOT_INSTALLED = "Pandoc is not installed on the server. Please contact your administrator for assistance."
    INCORRECT_FORMAT = (
        lambda err="": f"Invalid format. Please use the correct format{err}"
    )
    RATE_LIMIT_EXCEEDED = "API rate limit exceeded"

    MODEL_NOT_FOUND = lambda name="": f"Model '{name}' was not found"
    OPENAI_NOT_FOUND = lambda name="": "OpenAI API was not found"
    CLAUDE_NOT_FOUND = lambda name="": "Claude API was not found"
    OLLAMA_NOT_FOUND = "WebUI could not connect to Ollama"
    CREATE_API_KEY_ERROR = "Oops! Something went wrong while creating your API key. Please try again later. If the issue persists, contact support for assistance."

    EMPTY_CONTENT = "The content provided is empty. Please ensure that there is text or data present before proceeding."

    DB_NOT_SQLITE = "This feature is only available when running with SQLite databases."

    INVALID_URL = (
        "Oops! The URL you provided is invalid. Please double-check and try again."
    )

    WEB_SEARCH_ERROR = (
        lambda err="": f"{err if err else 'Oops! Something went wrong while searching the web.'}"
    )

    INVALID_OTP = "The OTP entered is invalid."
    PROFILE_EXISTING_CHATS = "There are existing chats using this profile."

    EXISTING_CHAT_SUBMISSION = "You have already submitted an attempt for this assignment"
    DEADLINE_CHAT_SUBMISSION = "The deadline for submission has passed"

    INVALID_EVAL_TITLE = "Evaluation titles must be at most 255 characters long."
    EVAL_TITLE_TAKEN = lambda name="": f"The evaluation title {name} is already taken."
    INVALID_EVAL_DELETION = lambda profiles=[]: f"This evaluation cannot be deleted as the profile{'s' if len(profiles) > 1 else ''} {', '.join(profiles)} {'are' if len(profiles) > 1 else 'is'} assigned to it."

    USER_IS_INSTRUCTOR = "User is an instructor of a class and cannot be deleted. Reassign the instructor and retry."
