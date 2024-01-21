from app.controllers.pinecone.dbHandler import db_update

def data_checking(data:dict, items_checklist:list, metadata_checklist:list)->dict:
  '''
  - Data quality check for data going to Pinecone database.
  :Params:
  - data: JSON object from web scrapper to store in Pinecone.
    JSON object in the following format:
                      {"documents":{
                        "items": [
                            {"text": "example", "metadata": {"title": 1, "id": 1, "link": 1}},
                            {"text": "example2", "metadata": {"title": 2, "id": 2, "link": 2}}
                        ],
                        "type": "article"
                    }}
  - items_checklist: list of items to check in second layer of JSON data
  - metadata_checklist: list of metadata to check in third layer of JSON data

  Output: Successful or error message in dict format: {'msg':'succcess', 'error_list':[]}
  '''
  error_list = []
  json_keys_to_check = ["items", "type"]
  items_keys_to_check = items_checklist
  metadata_keys_to_check = metadata_checklist
  for key in json_keys_to_check:
    if key not in data.keys():
      return {'msg':f"{key} missing! An article document needs to have {key}!", 'error_list': [f"{key} missing! A document needs to have {key}!"]}
  for index, item in enumerate(data['items']):
    try:
      for key in items_keys_to_check:
        if key not in item:
          error_list.append(f"Index {index} - {key} missing! An article document items needs to have {key}!")
      for key in metadata_keys_to_check:
        if key not in item['metadata'].keys():
          error_list.append(f"Index {index} - {key} missing! An article document metadata needs to have {key}!")
    except KeyError as e:
      continue
  if error_list == []:
    return {'msg': 'All keys exist in the JSON data!', 'error_list': None} 
  else:
    return {'msg': 'Mandatory properties missing in JSON data!', 'error_list': error_list}
  
def update_check(documents, items, metadata):
  error_message = data_checking(
        data=documents, 
        items_checklist=items, 
        metadata_checklist=metadata
        )
  if error_message['error_list'] == None:
    update_message = db_update(documents=documents['items'],
                        target_db=documents['type'])
    return update_message     
  else:
    return error_message