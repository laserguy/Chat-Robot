import os

# OPENAI_BASED_HANDLER

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ENGLINE = "text-davinci-003"
TEMPERATURE = 0.5
MAX_TOKENS = 60      
TOP_P = 0.3
FREQUENCY_PENALTY = 0.5
PRESENCE_PENALTY = 0.0


# HUGGINGFACE BASED HANDLER

HUGGINGFACE_ENGINE = "microsoft/DialoGPT-medium"   # By default use this
FACEBOOK_ENGINE  = "facebook/blenderbot-400M-distill"  # This runs bit slow with CPU, runs faster on the GPU
GODEL_ENGINE = "microsoft/GODEL-v1_1-large-seq2seq"
     
            
# ERROR MESSAGES

NO_INTERNET_CONNECTION = "No internet Connection"
GENERIC_MESSAGE = "Some error occurred"
MODEL_NOT_IMPLEMENTED = "Model doesn't implment context, use Blenderbot model for conversation with context"
