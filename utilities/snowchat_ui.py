import html
import re
import openai

import streamlit as st
from langchain.callbacks.base import BaseCallbackHandler

def message_func(text, is_user=False):
    '''
    This function is used to display the messages in the chatbot UI.
    
    Parameters:
    text (str): The text to be displayed.
    is_user (bool): Whether the message is from the user or the chatbot.
    key (str): The key to be used for the message.
    avatar_style (str): The style of the avatar to be used.
    '''
    if is_user:
        avatar_url = "https://avataaars.io/?avatarStyle=Transparent&topType=ShortHairShortFlat&accessoriesType=Prescription01&hairColor=Auburn&facialHairType=BeardLight&facialHairColor=Black&clotheType=Hoodie&clotheColor=PastelBlue&eyeType=Squint&eyebrowType=DefaultNatural&mouthType=Smile&skinColor=Tanned"
        message_alignment = "flex-end"
        message_bg_color = "linear-gradient(135deg, #00B2FF 0%, #006AFF 100%)"
        avatar_class = "user-avatar"
        st.write(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%;">
                        {text}
                    </div>
                            <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />

                </div>
                """, unsafe_allow_html=True)  
    else:
        avatar_url = "https://avataaars.io/?avatarStyle=Transparent&topType=WinterHat2&accessoriesType=Kurt&hatColor=Blue01&facialHairType=MoustacheMagnum&facialHairColor=Blonde&clotheType=Overall&clotheColor=Gray01&eyeType=WinkWacky&eyebrowType=SadConcernedNatural&mouthType=Sad&skinColor=Light"
        message_alignment = "flex-start"
        message_bg_color = "#71797E"
        avatar_class = "bot-avatar"
        st.write(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                    <img src="{avatar_url}" class="{avatar_class}" alt="avatar" />
                    <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%;">
                        {text} \n </div>
                </div>
                """, unsafe_allow_html=True)  


def reset_chat_history():
    '''
    This function is used to reset the chat history.
    '''
    st.session_state['generated'] = ["Hello! Ask me about your database tables and I will give you the answers. Remember to be specific in your wording. ❄️🔍"]  
    st.session_state['past'] = ["Hi..."]
    st.session_state["stored_session"] = []
    st.session_state['messages'] = [("Hello! I'm a chatbot designed to help you with Snowflake Database.")]  

def format_message(text):
    """
    This function is used to format the messages in the chatbot UI.

    Parameters:
    text (str): The text to be formatted.
    """
    text_blocks = re.split(r"```[\s\S]*?```", text)
    code_blocks = re.findall(r"```([\s\S]*?)```", text)

    text_blocks = [html.escape(block) for block in text_blocks]

    formatted_text = ""
    for i in range(len(text_blocks)):
        formatted_text += text_blocks[i].replace("\n", "<br>")
        if i < len(code_blocks):
            formatted_text += f'<pre style="white-space: pre-wrap; word-wrap: break-word;"><code>{html.escape(code_blocks[i])}</code></pre>'

    return formatted_text


# can be removed with better prompt
def extract_code(text) -> str:
    '''
    This function is used to extract the SQL code from the user's input.
    
    Parameters:
    text (str): The text to be processed.
    
    Returns:
    str: The SQL code extracted from the user's input.
    '''
    if len(text) < 5:
        return None
    # Use OpenAI's GPT-3.5 to extract the SQL code
    response = openai.ChatCompletion.create(
    model='gpt-3.5-turbo',
    messages=[
        {'role': 'user', 'content': f"Extract only the code do not add text or any apostrophes or any sql keywords \n\n{text}"},  
    ],
    # stream=True
    )

    # Extract the SQL code from the response
    sql_code = response.choices[0].message.content

    return sql_code

class StreamlitUICallbackHandler(BaseCallbackHandler):
    def __init__(self):
        # Buffer to accumulate tokens
        self.token_buffer = []
        self.placeholder = None
        self.has_streaming_ended = False

    def _get_bot_message_container(self, text):
        """Generate the bot's message container style for the given text."""
        avatar_url = "https://avataaars.io/?avatarStyle=Transparent&topType=WinterHat2&accessoriesType=Kurt&hatColor=Blue01&facialHairType=MoustacheMagnum&facialHairColor=Blonde&clotheType=Overall&clotheColor=Gray01&eyeType=WinkWacky&eyebrowType=SadConcernedNatural&mouthType=Sad&skinColor=Light"
        message_alignment = "flex-start"
        message_bg_color = "#71797E"
        avatar_class = "bot-avatar"
        formatted_text = format_message(text)
        container_content = f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px; justify-content: {message_alignment};">
                <img src="{avatar_url}" class="{avatar_class}" alt="avatar" style="width: 50px; height: 50px;" />
                <div style="background: {message_bg_color}; color: white; border-radius: 20px; padding: 10px; margin-right: 5px; max-width: 75%; font-size: 14px;">
                    {formatted_text} \n </div>
            </div>
        """
        return container_content

def is_sql_query(text: str) -> bool:
    """
    Checks if the input text is likely an SQL query.

    :param text: input text
    :return: True if the input is likely an SQL query, False otherwise
    """
    # Define a list of common SQL keywords
    keywords = [
        "SELECT", "FROM", "WHERE", "UPDATE", "INSERT", "DELETE", "JOIN",
        "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "UNION", "CREATE",
        "ALTER", "DROP", "TRUNCATE", "EXPLAIN", "WITH" , "INNER JOIN"
    ]


    # Create a single regular expression pattern to search for all keywords
    pattern = r'\b(?:' + '|'.join(keywords) + r')\b'

    # Check if any of the keywords are present in the input text (case-insensitive)
    if re.search(pattern, text, re.IGNORECASE):
        return True

    return False
