from typing import Annotated
from langchain_core.tools import tool 

# example tool for datetime
from datetime import datetime
@tool 
def get_current_time():
  """get the current date and time"""
  return datetime.now()

# example tool for weather
import random
@tool 
def get_weather(location: Annotated[str, "The city and state, e.g. San Francisco, CA"]) -> str:
  """get the current weather in a given location"""
  return "The current temperature in {} is {}°F".format(location, random.randint(-50, 105))




