from math import ceil

import text_processing as tp

import configparser

import openai

class Chat:
    """
    A class to manage the chat.
    """
    def __init__(self):
        # Setting up the configurations.
        config = configparser.ConfigParser()
        config.read("settings/config.ini")

        # Loading the settings.
        self.temperature = config.getfloat("GPT Settings", "temperature")
        self.api_key_path = config.get("GPT Settings", "api_key_path")
        self.max_tokens = config.getint("GPT Settings", "max_tokens")
        self.model = config.get("GPT Settings", "model")
        self.prompt = config.get("GPT Settings", "prompt")

        self.completion_length = self.max_tokens

    def generate_response(self, arg):
        """
        Generates a response from the GPT API.
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{'role': 'system', 'content': self.generate_prompt(argument=arg)}],
            temperature=self.temperature,
            max_tokens=self.completion_length,
        )
        return response['choices'][0]['message']['content']

    def generate_prompt(self, argument: str) -> str:
        # Add the argument to the prompt defined in the config file.
        prompt = tp.preprocess(self.prompt + argument)

        # Calculate the number of tokens we pass into the gpt.
        # The number is always bigger than the actual tokenization, but it doesn't return an error this way.
        tokens_by_chars: int = ceil(len(prompt)/4)

        # Calculate the maximal number of tokens available to complete the prompt.
        self.completion_length = self.max_tokens - tokens_by_chars

        return prompt

# # Saving the original text passed.
# pdf.add_text(f"Original text: {arg}\n")

# # Run GPT
# response = chat.generate_response(arg=arg)
# pdf.add_text(f"GPT response: {response}")

# pdf.save_pdf()