import os
import openai



__author__ = "Eden Wu"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"

class GptAPI():
    """This model is for semantic processing any text with openai GPT model."""
    def __init__(self, key):
        openai.api_key = key
        self.model_list = openai.Model.list()
        
    def chat(self, model, input_line):
        """Chat with GPT, return is a string
        Input:
            model: the valid model returned by openai server, check with .model_list (in string)
            input_line: input string
        """
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "user", "content": input_line}
            ])
        
        return completion.choices[0].message