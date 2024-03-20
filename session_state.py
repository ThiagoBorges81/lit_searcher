# session_state.py
import  streamlit                   as st
import  streamlit.report_thread     as ReportThread
from    streamlit.server.server     import Server

class SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key,val)

def get(**kwargs):
    # Get session object from  Streamlit
    session_id = ReportThread.getreport_ctx().session_id
    session = Server.get_current()._get_session_info(session_id).session

    # Create the SessionState if it doesn't exist
    if not hasattr(session, "_custom_session_state"):
        session._custom_session_state = SessionState(**kwargs)

    return session._custom_session_state