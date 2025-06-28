import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def load_authenticator():
    with open("users.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    return authenticator
