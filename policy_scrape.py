import requests
import numpy as np
import pandas as pd
import lxml.html as lh

"""
Basic web scraping of policy data from IEA website. Not the most general/robust but gets the job done for this task
"""

url_base = "https://www.iea.org/policies"
class_tag_prefix = "m-policy-listing-item__col m-policy-listing-item__col--"
num_pages = 187
# Initialise data frame to add to
column_headings = ['policy', 'country', 'year', 'status', 'jurisdiction']
policy_data_arr = np.empty((1,len(column_headings)), dtype='<U113')

for i in range(num_pages):
    try:
        url = url_base+f"?page={i+1}" ##the apprpriate url variable
        page = requests.get(url)
        page_content=lh.fromstring(page.content)
        page_data = []
        for heading in column_headings:
            class_tag = class_tag_prefix+heading
            class_tag_pos = page_content.find_class(class_tag)
            row_stripped =  [x.text_content().replace('\n', '').replace('\t', '').replace('\r', '').strip(' ') for x in class_tag_pos]
            page_data.append(row_stripped)
        ## reshape sublists for easy storing in DF
        out=[ [category[i] for category in page_data] for i in range(len(page_data[0])) ]
        s= np.array(out)
        policy_data_arr = np.vstack((policy_data_arr, s))
    except:
        print("Page probably doesn't exist")

    print(f"Progress: {i/num_pages}")

## Place into DataFrame object
policy_data = pd.DataFrame(policy_data_arr, columns=column_headings)
policy_data.to_csv("Policy_data.csv")

