from flask import session
## My own modules and functions ##

def clearSession(sessionToClear):
    for record in sessionToClear:
        print("XXXXXXXXXXXXXXXXXXXXXXX")
        print(record)
        print(session.get(record))
        if session.get(record):
                session.pop(record, None)
