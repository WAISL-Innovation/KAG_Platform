import os
import sys
import logging

# Here we set the formate or look and feel of my loog. first timestamp then log lavel like info/error/exception/warning
# then module name means class name then the log message will display. If main.py run then labelname will be root
logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"
log_dir = "logs" # folder name
log_filepath = os.path.join(log_dir,"running_logs.log") # set the current directory to create the log with name "running_logs.log"
os.makedirs(log_dir, exist_ok=True) # Create the log directory and file.


# Setting the log details like here we set only Info lavel will be and set the above decleared formate then
# where file it is for write the log and StreamHandler() is use for when we run the project using terminal
# still log should display on console also.
logging.basicConfig(
    level= logging.INFO, 
    format= logging_str,

    handlers=[
        logging.FileHandler(log_filepath),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("RAG-Stack") # here we set the logger name as "RAG-Stack" and this is the main logger