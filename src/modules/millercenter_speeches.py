# import json, requests, sys
# from src.modules.paths_reference import DATA_PATH


# endpoint = "https://api.millercenter.org/speeches"
# out_file = "millercenter_speeches.json"
# out_path = DATA_PATH /"raw"/ out_file

# r = requests.post(url=endpoint)
# data = r.json()
# items = data['Items']

# while 'LastEvaluatedKey' in data:
#     parameters = {"LastEvaluatedKey": data['LastEvaluatedKey']['doc_name']}
#     r = requests.post(url = endpoint, params = parameters)
#     data = r.json()
#     items += data['Items']
#     print(f'{len(items)} speeches')

# with open(out_path, "w") as out:
#     out.write(json.dumps(items))
#     print(f'wrote results to file: {out_file} on Raw directory')
import json
import requests
from pathlib import Path

def download_data(data_path:Path, out_file="millercenter_speeches.json"):
    endpoint = "https://api.millercenter.org/speeches"
    out_path = data_path / "raw" / out_file

    def fetch_speeches():
        items = []
        data = {'LastEvaluatedKey': None}
        
        while True:
            parameters = {"LastEvaluatedKey": data['LastEvaluatedKey']['doc_name']} if 'LastEvaluatedKey' in data else None
            r = requests.post(url=endpoint, params=parameters)
            data = r.json()
            items += data['Items']
            print(f'{len(items)} speeches')
            
            if 'LastEvaluatedKey' not in data:
                break
        
        return items

    speeches = fetch_speeches()

    with open(out_path, "w") as out:
        json.dump(speeches, out)
        print(f'Wrote results to file: {out_file} in Raw directory')

    return speeches