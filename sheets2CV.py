#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Tue Aug 15 11:08:21 2023

# @author: karinmorandell
#"""

import importlib
import pandas as pd 
import re
import os
import subprocess

import platform
from sys import platform as sys_platform

# STEP 1: Read the Google Sheet data as dataframe
def get_data_from_sheet(sheet_id: str):
    
    # Get params
    sheet_name = 'params'
    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'    
    
    PARAMS = getParams(sheet_url)
    
    # Get data

    DATA, DF= getData(sheet_id,PARAMS)
    
    
    return DATA, PARAMS



def getParams(sheet_url):
    # Read a CSV file from the given URL and create a DataFrame
    DF = pd.read_csv(sheet_url)
    # Filter the DataFrame for rows where the 'selection' column is 1
    DF = DF[DF['selection'] == 1]
    # Drop the 'selection' column as it's no longer needed after filtering
    DF.drop(columns=['selection'], inplace=True)
    # Reset the index of the DataFrame to have a continuous index after filtering
    DF = DF.reset_index(drop=True)
    # Get the number of PDFs/rows after filtering
    nPDFs = len(DF)
    
    # Initialize an empty list to store parameters for each PDF
    PARAMS = list()
    
    # Loop through each row in the DataFrame
    for i in range(nPDFs):
        # Initialize a dictionary to store the parameters for the current PDF
        params = {
            'template_name': DF['template_name'][i],  # Get the template name from the DataFrame
            'pdf_name': DF['pdf_name'][i],  # Get the PDF name from the DataFrame
        }
        
        params['save_folder'] = "CVs/"#default
        
        # Add '.pdf' extension if it's not present in the pdf_name
        if re.search(r'\.pdf$', params['pdf_name']):
            params['save_path'] = params['save_folder'] + params['pdf_name']
        else:
            params['save_path'] = params['save_folder'] + params['pdf_name'] + ".pdf"
    
        # Ensure that the template_name ends with '.py' extension
        if not re.search(r'\.py$', params['template_name']):
            params['template_name'] = params['template_name'] + ".py"
            
        # Construct the full path to the template file
        params['template_path'] = "templates/" + params['template_name']
        
        # Set a default 'sheet' parameter from the DataFrame
        params['sheet'] = DF['sheet_name'][i]
        
        # Get additional parameters from the 'params' column, split by semicolons
        params_data = DF['params'][i]
        params_list = params_data.split(';')
        
        # Loop through each parameter in the list
        for item in params_list:
            if item.strip():  # Ensure that the item is not just whitespace
                # Split the parameter by the equals sign to get name and value
                param_name, param_value = item.split('=')
                # Add the parameter name and value to the params dictionary
                params[param_name.strip()] = param_value.strip()
        
        ## Correct params if necessary
        
        # Check if the 'color' parameter is a hex color code
        if params.get('color', '').startswith('#'):
            HEX = params['color']
            # Convert the hex color code to an RGB tuple
            RGB = hex2rgb(HEX)
            # Add the RGB color tuple to the params dictionary
            params['color_rgb'] = RGB
            # Add the original hex color code to the params dictionary
            params['color_hex'] = HEX
        
        if not params['save_folder'][-1]=='/':
            params['save_folder'] = params['save_folder']+'/'
        
        if not os.path.exists(params['save_folder']):
          os.mkdir(params['save_folder'])  
        
        # Add '.pdf' extension if it's not present in the pdf_name
        if re.search(r'\.pdf$', params['pdf_name']):
            params['save_path'] = params['save_folder'] + params['pdf_name']
        else:
            params['save_path'] = params['save_folder'] + params['pdf_name'] + ".pdf"
            
        # vertical_offset : Make sure the variable is an float
        if 'vertical_offset' in params.keys():
            params['vertical_offset'] = float(params['vertical_offset'])
       
                        
            
        # Append the parameters for the current PDF to the PARAMS list
        PARAMS.append(params)
    
    # Return the list of parameters for all PDFs
    return PARAMS



def getData(sheet_id,PARAMS):
    
    DATA = []
    
    for params in PARAMS:
        sheet_name = params["sheet"]
        sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        DF = pd.read_csv(sheet_url)
        data= formatData2(DF)
        DATA.append(data)
        
    return DATA,DF


def formatData2(DF):
    
    # First column of dataframe DF is set as rownames in data frame
    

    # Get rid of rows that are not included
    DF = DF[DF['include'] == 1]
    DF = DF.drop(columns=['include'])
    df = DF.set_index('section',inplace=False)
    sections = df.index
    sections = list(set(list(sections)))# unique sections

    
    # Initialize the data dict
    data = dict()
    
    # Create a personal info dict ( data access : personal_info['name'])
    personal_info = df.loc['Personal details']
    personal_info = personal_info.set_index('fieldname')
    personal_info = personal_info.filter(items=['fieldname', 'fieldvalue'])
    personal_info = personal_info['fieldvalue'].to_dict()
    data['contact'] = personal_info
    
    # Create an education dataframe
    education_data =  df.loc['Education']
    education_data = education_data.reset_index(drop = True)
    education_data = education_data.filter(items=[ 'fieldvalue' ,'datestart' ,'dateend' ,'location'])
    data['education']=education_data

    # Create an experience dataframe
    if 'Professional experience' in sections:
        exp_df = df.loc['Professional experience']
        exp_df = exp_df.reset_index(drop = True)
        exp_df = exp_df.set_index('fieldname')
    
    
    
        # Find number of experiences
        ranks = exp_df['rank'].tolist()
        nItems = int(max(ranks))
    
        # Iterate over each experience item
        exp_dict = list()
        for iexp in range(1, nItems+1):
            thosefields = [(rank == iexp) for rank in ranks]
    
            this_exp = exp_df.loc[thosefields]
            
    
            thisexp_dict = {
                'position': this_exp.loc['position','fieldvalue'],
                'company': this_exp.loc['company','fieldvalue'],
                'datestart': this_exp.loc['position','datestart'],
                'dateend': this_exp.loc['position','dateend'],
                'location': this_exp.loc['position','location'],
                'descriptions': list() ,
                'publications':list() ,
                'spacer':list(),
            }
            
            # Extract description rows
            fields = this_exp.index.tolist()
            i4 = [f.startswith('description') for f in fields]
            those_descriptions= this_exp[i4]
            ndes = len(those_descriptions) 
    
            if ndes !=0:
                for ides in range(1,ndes+1):
                    thisdes =  this_exp.loc[f'description{ides}'    ,'fieldvalue']
                    thisexp_dict['descriptions'].append(thisdes)        
    
            
            # Extract and process publications
            i4 = [(f.startswith('publication') and f.endswith('_text')) for f in fields]            
            those_publications = this_exp[i4]
            npub = len(those_publications)
    
            if npub !=0:
                
                for ipub in range(1,npub+1):
                    thispub = {
                        'text'  : this_exp.loc[f'publication{ipub}_text'    ,'fieldvalue'],
                        'url'   : this_exp.loc[f'publication{ipub}_url'     ,'fieldvalue']
                        }                
    
                    thisexp_dict['publications'].append(thispub)        
            
            exp_dict.append(thisexp_dict)
    
            # Extract and process achievements
            i4 = [f.startswith('achievements') for f in fields]   
            
            those_achievements = this_exp[i4]

            if len(those_achievements) ==1:
                thisexp_dict['achievements'] = this_exp.loc['achievements','fieldvalue']
            elif len(those_achievements)>1:
                thisexp_dict['achievements'] = this_exp.loc['achievements','fieldvalue'].tolist()
                
            # Extract spacer
            i4 = [f.startswith('spacer') for f in fields]  
            those_items = this_exp[i4]
            if len(those_items) !=0:
                thisexp_dict['spacer'] = float(those_items.loc['spacer','fieldvalue'])
                
                
        data['experience']=exp_dict
      

    ####
    # key_skills
    K = df.loc['Key skills']
    K.set_index('fieldname',inplace=True)
    
    ranks = K['rank'].tolist()
    nItems = int(max(ranks))
    key_skills = list()
    for i in range(1,nItems+1):
        
        i4item = [rank==i for rank in ranks]
        k = K[i4item]
        key_skill={
            'skill' : k.loc['skill','fieldvalue'],
            'description' : k.loc['description','fieldvalue'],
            }
        key_skills.append(key_skill)
        
    data['key_skills'] = key_skills

    ####
    # tech_skills
    data['tech_skills'] = df.loc['Tech languages','fieldvalue']
  
    ####
    # skills
    data['skills'] = df.loc['Skills','fieldvalue']    
    
    ####
    # languages
    data['languages'] = df.loc['Langages','fieldvalue']
    
    ####
    # about_me
    dftemp=df.set_index('fieldname',inplace=False)
    data['about_me'] = {
        'personality' : dftemp.loc['Personality','fieldvalue'],
        'interests' : dftemp.loc['Interests','fieldvalue'],
        }
    
    ####
    # references
    if 'References' in sections:
        data['references']= df.loc['References','fieldvalue']
    
    
    ####
    # Awards
    if 'Awards' in sections:
        # Create a dataframe
        data_aw =  df.loc['Awards']
        data_aw = data_aw.reset_index(drop = True)
        data_aw = data_aw.filter(items=[ 'fieldvalue' ,'datestart' ,'dateend' ,'location'])
        data['awards']=data_aw    
        
    ####
    # Conferences
    if 'Conferences' in sections:
        # Create a dataframe
        data_conf =  df.loc['Conferences']
        data_conf = data_conf.reset_index(drop = True)
        data_conf = data_conf.filter(items=[ 'fieldvalue' ,'datestart' ,'dateend' ,'location'])
        data['conferences']=data_conf        
        
    return data

def formatData(DF):
    
    # First column of dataframe DF is set as rownames in data frame
    

    # Get rid of rows that are not included
    DF = DF[DF['include'] == 1]
    DF = DF.drop(columns=['include'])
    df = DF.set_index('section',inplace=False)
    sections = df.index
    sections = list(set(list(sections)))# unique sections

    
    # Initialize the data dict
    data = dict()
    
    # Create a personal info dict ( data access : personal_info['name'])
    personal_info = df.loc['Personal details']
    personal_info = personal_info.set_index('fieldname')
    personal_info = personal_info.filter(items=['fieldname', 'fieldvalue'])
    personal_info = personal_info['fieldvalue'].to_dict()
    data['contact'] = personal_info
    
    # Create an education dataframe
    
    education_data =  df.loc['Education']
    education_data = education_data.reset_index(drop = True)
    education_data = education_data.filter(items=[ 'fieldvalue' ,'datestart' ,'dateend' ,'location'])
    data['education']=education_data

    # Create an experience dataframe
    if 'Professional experience' in sections:
        exp_df = df.loc['Professional experience']
        exp_df = exp_df.reset_index(drop = True)
        exp_df = exp_df.set_index('fieldname')
    
    
    
        # Find number of experiences
        allrows = exp_df.index.tolist()
        last_row_name = exp_df.index.tolist()[-1]
        n_exp = int(re.findall('item([0-9]*)_',last_row_name)[0])
    
        # Iterate over each experience item
        exp_dict = list()
        for i in range(1, n_exp+1):
            thosefields = [index for index in allrows if index.startswith(f'item{i}_')]
    
            this_exp = exp_df.loc[thosefields]
            
    
    
    
            thisexp_dict = {
                'position': this_exp.loc[f'item{i}_position','fieldvalue'],
                'company': this_exp.loc[f'item{i}_company','fieldvalue'],
                'datestart': this_exp.loc[f'item{i}_position','datestart'],
                'dateend': this_exp.loc[f'item{i}_position','dateend'],
                'location': this_exp.loc[f'item{i}_position','location'],
                'descriptions': list() ,
                'publications':list() ,
                'spacer':list(),
            }
            
            # Extract description rows
            those_descriptions = [index for index in allrows if index.startswith(f'item{i}_description')]
    
            ndes = len(those_descriptions) 
    
            if ndes !=0:
                for ides in range(1,ndes+1):
                    thisdes =  this_exp.loc[f'item{i}_description{ides}'    ,'fieldvalue']
                    thisexp_dict['descriptions'].append(thisdes)        
    
            
            # Extract and process publications
            those_publications = [index for index in allrows if index.startswith(f'item{i}_publication') and index.endswith('_text')]
            npub = len(those_publications)
    
            if npub !=0:
                
                for ipub in range(1,npub+1):
                    thispub = {
                        'text'  : this_exp.loc[f'item{i}_publication{ipub}_text'    ,'fieldvalue'],
                        'url'   : this_exp.loc[f'item{i}_publication{ipub}_url'     ,'fieldvalue']
                        }                
    
                    thisexp_dict['publications'].append(thispub)        
            
            exp_dict.append(thisexp_dict)
    
            # Extract and process achievements
            those_achievements = [index for index in allrows if index.startswith(f'item{i}_achievements') ]
            nach = len(those_achievements)
            if nach !=0:
                thisexp_dict['achievements'] = this_exp.loc[f'item{i}_achievements','fieldvalue']
                
            # Extract spacer
            this_spacer = [index for index in allrows if index.startswith(f'item{i}_spacer') ]
            if len(this_spacer) !=0:
                thisexp_dict['spacer'] = float(this_exp.loc[f'item{i}_spacer','fieldvalue'])
                
                
        data['experience']=exp_dict
      

    ####
    # key_skills
    k = df.loc['Key skills']
    k.set_index('fieldname',inplace=True)
    last_row_name = k.tail(1).index.tolist()[0]
    nkskills = int(re.findall('item([0-9]*)_',last_row_name)[0])
    key_skills = list()
    for i in range(1,nkskills+1):
        key_skill={
            'skill' : k.loc[f'item{i}_skill','fieldvalue'],
            'description' : k.loc[f'item{i}_description','fieldvalue'],
            }
        key_skills.append(key_skill)
        
    data['key_skills'] = key_skills

    ####
    # tech_skills
    data['tech_skills'] = df.loc['Tech languages','fieldvalue']
  
    ####
    # skills
    data['skills'] = df.loc['Skills','fieldvalue']    
    
    ####
    # languages
    data['languages'] = df.loc['Langages','fieldvalue']
    
    ####
    # about_me
    dftemp=df.set_index('fieldname',inplace=False)
    data['about_me'] = {
        'personality' : dftemp.loc['Personality','fieldvalue'],
        'interests' : dftemp.loc['Interests','fieldvalue'],
        }
    
    ####
    # references
    if 'References' in sections:
        data['references']= df.loc['References','fieldvalue']
    
    
    ####
    # Awards
    if 'Awards' in sections:
        data['awards']= df.loc['Awards','fieldvalue']    


    return data

def hex2rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))    

# STEP 2: Populate the CV using ReportLab
def generate_cv(DATA, PARAMS):
    

    for params,data in zip(PARAMS,DATA):
        module_path = params['template_path']

        module_path = module_path.replace('/','.').replace('.py', '')
        module = importlib.import_module(module_path)
        generatePDFresume = module.generatePDFresume

        generatePDFresume(data, params)
        
        openMyCV(params['save_path'])


        print("=== > CV Created Successfully! ____ "+ params['save_path'])




def openMyCV(save_path):
    # Check the operating system
    if sys_platform == "darwin":
        # macOS
        subprocess.run(["open", save_path], check=True)
        folder_path = os.path.dirname(save_path)
        subprocess.run(["open", folder_path], check=True)
    elif sys_platform == "win32":
        # Windows
        os.startfile(save_path)
        folder_path = os.path.dirname(save_path)
        os.startfile(folder_path)
    elif '/content' in save_path:
        # Google Colab - Provide a download link instead of opening
        print(f"Download your file from: {save_path}")
        # Optionally, you can use Google Colab's files.download to trigger a download
        from google.colab import files
        files.download(save_path)
    else:
        # Other Linux-based systems (non-GUI)
        print(f"File saved at: {save_path}")


def extract_spreadsheet_id(url):
    """
    Extracts the Google Spreadsheet ID from a given URL.

    Args:
    url (str): The URL of the Google Spreadsheet.

    Returns:
    str: The extracted Spreadsheet ID.
    """
    # Regular expression pattern to match the Google Spreadsheet ID
    pattern = r"/spreadsheets/d/([a-zA-Z0-9-_]+)"
    
    # Search for the pattern in the URL
    match = re.search(pattern, url)

    # If a match is found, return the Spreadsheet ID
    if match:
        return match.group(1)
    else:
        return "Invalid URL"




 

# Main function
def main(**kwargs):  
    
    print("===== 1/3) GET GOOGLE SPREADSHEET ID ....")
    if 'sheet_id' in kwargs:
        sheet_id = kwargs['sheet_id']
    elif 'sheetURL' in kwargs:
        # Extract the sheet ID from the URL
        # Assuming the URL format is standard Google Sheets format
        sheet_id = extract_spreadsheet_id(kwargs['sheetURL'])    
    else:
        sheet_id = '1Kkdkra9Yoli7kWrP8TaMRjocRR29Kz2PYxHkYLrUzXo'# github sheet
        print('Using personal sheet for generating CV.')
        sheet_id = '1pWPaT7KlnJKEzZf2hBt716YtVEOcr6f2l7rAe8MFKP8'# personal sheet

    print("===== 2/3) GET DATA FROM SHEET ....")
    DATA, PARAMS = get_data_from_sheet(sheet_id)
    
    
    print("===== 3/3) GENERATE CV ....")
    generate_cv( DATA, PARAMS )





if __name__ == "__main__":
    
    main()


