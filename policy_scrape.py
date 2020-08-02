import requests
import numpy as np
import pandas as pd
import lxml.html as lh
import time

"""
Basic web scraping of policy data from IEA website. Not the most general/robust but gets the job done for this task
"""

url_base = "https://www.iea.org"
class_tag_prefix = "m-policy-listing-item__col m-policy-listing-item__col--"
num_pages = 187
# Initialise data frame to add to
column_headings = ['policy', 'country', 'year', 'status', 'jurisdiction']
col_headins_2 = ["topics", "policy types", "sectors", "technologies", "end uses covered"]
policy_data_tot = []# = np.empty((1,len(column_headings+col_headins_2)), dtype='<U113')

for i in range(num_pages):
    policy_links = []
    try:
        url = url_base+f"/policies?page={i+1}" ##the apprpriate url variable
        page = requests.get(url)
        page_content=lh.fromstring(page.content)
        page_data = []
        page_categories = []
        for heading in column_headings:
            class_tag = class_tag_prefix+heading
            class_tag_pos = page_content.find_class(class_tag)
            row_stripped =  [x.text_content().replace('\n', '').replace('\t', '').replace('\r', '').strip(' ') for x in class_tag_pos]
            page_data.append(row_stripped)
        ## reshape sublists for easy storing in DF
        #out=[ [category[i] for category in page_data] for i in range(len(page_data[0])) ]
        #s= np.array(out)
        #policy_data_arr = np.vstack((policy_data_arr, s))

        ## Now lets extract the link
        for e, attr, link, pos in page_content.iterlinks():
            if link.startswith("/policies/") and not link.startswith("/policies/about") :
                policy_links.append(link)

        ## Follow link and yield the tags
        for p in policy_links:
            time.sleep(4)
            page_policy = requests.get(url_base+p)
            page_policy_content=lh.fromstring(page_policy.content)
            tag_pos = page_policy_content.find_class("o-policy-content__list")
            stripped_data =[list(filter(None, i.text_content().replace("\n","").replace("\t","").replace("\r", "").strip(' ').replace("Remove Filter","").split("  ")))for i in tag_pos]
            data_pretty = [ [', '.join(x[1:]) for x in stripped_data if x[0].lower() == head] for head in col_headins_2]
            data_pretty = [ x[0] if x != [] else "" for x in data_pretty]
         #   print(data_pretty)

            page_categories.append(data_pretty)

        out0 = [ [category[i] for category in page_data] for i in range(len(page_data[0])) ] #+ page_categories
        out = [ out0[i] + page_categories[i] for i in range(len(out0))] 
        policy_data_tot = policy_data_tot + out
    except:
        print("Page probably doesn't exist")




            

    print(f"Progress: {i/num_pages}")

## Place into DataFrame object
policy_data = pd.DataFrame(policy_data_tot, columns=column_headings+col_headins_2)
policy_data.to_csv("Policy_data.csv")

