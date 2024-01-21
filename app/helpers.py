import json
import datetime
import pickle
import pytz

def logToFile(data):
  with open('log.txt', 'a') as f:
    f.write(f'{datetime.datetime.utcnow()} - {json.dumps(data)}\n')
    
def read_path(file_path: str):
  with open(file_path, 'r') as json_file: 
    data = json.load(json_file)
  return data
   
def write_path(file_path: str, data: list[dict]):
  with open(file_path, 'w') as json_file: 
    json.dump(data, json_file, indent=2)

def get_time():
  '''
  - To obtain current time for noting the scheduler completed time.
  Timezone: Malaysia
  '''
  malaysia_timezone = pytz.timezone('Asia/Kuala_Lumpur')
  utc_now = datetime.datetime.utcnow()
  malaysia_now = utc_now.replace(tzinfo=pytz.utc).astimezone(malaysia_timezone)
  formatted_time = malaysia_now.strftime("%Y-%m-%d %H:%M:%S %Z")
  return formatted_time