# Do initial testing of grabbing a single bug
# Be able to pull relevant fields and place into dataframe
# Write out this dataframe to json 
# once pipeline is solid, do larger batch
# once batches perform well, do repository, make sure to put wait calls in
# Assume to have 3 different jsons saved, SUSE, KDE, Gentoo
# Load jsons into dataframe, determine which statistics to report
# Create graphs and other relevant content for report

KDE_BASE_URL = "https://bugs.kde.org/show_bug.cgi?ctype=xml&id="
SUSE_BASE_URL = "https://bugzilla.suse.com/show_bug.cgi?ctype=xml"
GENTOO_BASE_URL = "https://bugs.gentoo.org/show_bug.cgi?ctype=xml&id="

import requests
import pandas as pd
from io import StringIO
from dateutil.parser import parse
import time

def get_ticket_as_xml(base_url, ticket_number):
  """
  get_ticket_as_xml
    queries url to pull xml formatted ticket information

  params: 
    base_url : string url pointing to xml ticket excluding the ticket number
    ticket_number: integer number of ticket to be requested

  returns:
    string : content of ticket page in xml, empty if ticket is not found
  """
  url = base_url + str(ticket_number)
  page = requests.get(url)
  if page.status_code == requests.codes.ok:
    return page.text
  else:
    return ""


def convert_xml_to_df(xml_text):
  """
  convert_xml_to_dict
    takes a text object containing xml ticket info and puts into dataframe
    needs to flatten the description / comments that are contained under 
    <long_desc><thetext>DESC/COMMENT</thetext></long_desc>

  params:
    xml_text : string ticket info as xml

  returns:
    pandas dataframe : ticket information or empty if text is empty
  """
  df = pd.DataFrame()

  if xml_text != "":
    df = pd.read_xml(StringIO(xml_text))

  return df


def scrape_repository(url, repo_name):  
  """
  scrape_repository
    loops through all tickets of a given url, converts to xml
    place into a dataframe and write out as a csv file

  params:
    url : string base url for xml page without ticket number
    repo_name : string name of site in url

  returns:
    nothing, could do bool to track success but ehh
  """
  df_list = []
  ticket_ids = [44, 44723, 58393, 65738, 87316, 95376, 125163, 185390, 253163, 415734]
  year = 0

  # loop through tickets
  for id in ticket_ids:
    
    xml_text = get_ticket_as_xml(url, id)
    df = convert_xml_to_df(xml_text)

    # only add if ticket exists and it's older than 2013
    if not df.empty and not 'error' in df:
      date_string = df['creation_ts'].values[0]
      ticket_year = parse(date_string).year
      if ticket_year < 2013:
        df_list.append(df)
        if ticket_year > year:
          year = ticket_year
          print(f"INFO: Repository: {repo_name} Year: {year}")            
    
    time.sleep(2)
  # end loop

  # combine back into dataframe
  final_df = pd.concat(df_list)

  #write out as csv
  final_df.to_csv(repo_name + ".csv", index=False)

scrape_repository(KDE_BASE_URL, "kde")
scrape_repository(SUSE_BASE_URL, "suse")
scrape_repository(GENTOO_BASE_URL, "gentoo")