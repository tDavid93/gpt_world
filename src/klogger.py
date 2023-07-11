from kafka import KafkaProducer
import datetime
import socket
import os 
from rich.console import Console
from rich.highlighter import Highlighter
from rich.text import Text

class LogHighlight():
    """Highlight log messages based on its log level."""
    
    base_style = "white"
    highlights = {
        "ERROR": "red",
        "WARNING": "yellow",
        "INFO": "blue",
        "DEBUG": "green",
        
    }
    info_highlights = {
        "ERROR": "red",
        "WARNING": "yellow"
    }
    
    def stylize(self, level :str ,name :str, action : str, arg : str):
        
        
        info_style = "white"
        final_text = Text()
        for level, style in self.highlights.items():
            if level.__contains__(level):
                final_text  = Text(level + ": ", style)
            if self.info_highlights.__contains__(level):
                info_style = self.info_highlights[level]
            final_text.append(name + "; ",info_style)
            final_text.append(action + " {",info_style)
            final_text.append(arg + "}",info_style)
        return final_text  
                
    

klogger_producer = KafkaProducer(bootstrap_servers=os.environ.get('KAFKA_SERVER_ADDRESS')) 
klogger_ip_address = socket.gethostbyname(socket.gethostname())
console = Console(highlight=True)
log_highlight = LogHighlight()
log_levels = [
    "ERROR",
    "WARNING",
    "INFO",
    "DEBUG",
    "DEFAULT"
]



BLACKLIST = [ 
]
LOGGING_LEVEL = "DEFAULT"
        
        
def klog( name, action, arg, level="INFO"):
    """Log a message to the kafka logging system."""
    
    if log_levels.index(level) > log_levels.index(LOGGING_LEVEL):
        return None
        
            #lOCAL LOGGING
    
    local_log = log_highlight.stylize(level, name, action, arg)
    console.log(local_log) 
        
    msg = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')};{name};{klogger_ip_address};{level};{name};{action};{arg}"
    #disabled for now
    #klogger_producer.send("log", msg.encode('utf-8'))
        
        