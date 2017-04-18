" This Module Imports data from a Ohmeda "

import logging
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler('./pulsi.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

from datetime import datetime
def create_event_from_output(line):
    "Takes the output form the Ohmeda and returns a event to loading into the database"

    #parse on " "
    parsed_string = line.strip().split(" ")

    #make sure we got a full record before we continue.
    #The first record read can often be a partial record.
    if len(parsed_string) == 4:
        currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        while parsed_string[0][0] == '\x00':
            print("nulls")
            parsed_string[0] = parsed_string[0][1:]

        spo2 = parsed_string[1]
        bpm = parsed_string[3]

        doc = {
            "date" : currentTime,
            "serial_number" : "ohmeda",
            "spo2" : spo2,
            "bpm" : bpm,
            "pi" : "--",
            "alarm" : "---"
        }
        return doc
    else:
        logger.error("Malformed line: '" + str(line) + "'")
        return None
