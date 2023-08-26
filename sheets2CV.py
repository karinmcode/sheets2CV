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


# STEP 1: Read the Google Sheet data as dataframe
def get_data_from_sheet(sheet_id: str):
    
    sheet_name = 'data'
    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    
    DF = pd.read_csv(sheet_url)
    data = formatData(DF)
    
    sheet_name = 'params'
    sheet_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    
    PARAMS = getParams(sheet_url)
    return DF, data, PARAMS

def getParams(sheet_url):
    DF = pd.read_csv(sheet_url)
    DF = DF[DF['selection']==1]
    DF.drop(columns=['selection'],inplace=True)
    # Resetting index after filtering
    DF = DF.reset_index(drop=True)
    nPDFs = len(DF)
    
    PARAMS = list()
    
    for i in range(0,nPDFs):
        params = dict()
        
        params = {
            'template_name'     : DF['template_name'][i],
            'pdf_name'          : DF['pdf_name'][i],
            
            }
        
        if re.search(r'\.pdf$',params['pdf_name']):
            params['save_path'] = "CVs/"+params['pdf_name']
        else:
            params['save_path'] = "CVs/"+params['pdf_name']+".pdf"
    
        match = re.search(  r'\.py$', params['template_name'])
        if not match: # params['template_name']='template_default'
            params['template_name'] = params['template_name']+".py"
            
        params['template_path'] = "templates/"+params['template_name']
        
        params_data = DF['params'][i]
        params_list = params_data.split(';')
        
        for index,item in enumerate(params_list):
            if item != '\n':
                param_name = item.split('=')[0]
                param_value = item.split('=')[1]
                params[param_name]=param_value
                
        PARAMS.append(params)
    
    
    return PARAMS


def formatData(DF):
    
    # First column of dataframe DF is set as rownames in data frame
    

    # Get rid of rows that are not included
    df = DF[DF['include'] == 1]
    df = df.drop(columns=['include'])
    df.set_index('section',inplace=True)
    
    # Create a personal info dict ( data access : personal_info['name'])
    personal_info = df.loc['Personal details']
    personal_info = personal_info.set_index('fieldname')
    personal_info = personal_info.filter(items=['fieldname', 'fieldvalue'])
    personal_info = personal_info['fieldvalue'].to_dict()
    
    # Create an education dataframe
    
    education_data =  df.loc['Education']
    education_data = education_data.reset_index(drop = True)
    education_data = education_data.filter(items=[ 'fieldvalue' ,'datestart' ,'dateend' ,'location'])
    
    
    # Create an experience dataframe
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

    ####
    # tech_skills
    tech_skills = df.loc['Tech languages','fieldvalue']
    
    ####
    # skills
    skills = df.loc['Skills','fieldvalue']    
    
    
    ####
    # langages
    langages = df.loc['Langages','fieldvalue']
    
    ####
    # about_me
    df.set_index('fieldname',inplace=True)
    about_me = {
        'personality' : df.loc['Personality','fieldvalue'],
        'interests' : df.loc['Interests','fieldvalue'],
        }   

    # pack information in data dictionary
    data = dict()
    data['contact'] = personal_info
    data['experience']=exp_dict
    data['education']=education_data
    data['key_skills'] = key_skills
    data['tech_skills'] = tech_skills
    data['skills'] = skills
    data['langages'] = langages
    data['about_me'] = about_me
    return data

# STEP 2: Populate the CV using ReportLab
def generate_cv(data, PARAMS):
    

    for params in PARAMS:
        module_path = params['template_path']

        module_path = module_path.replace('/','.').replace('.py', '')
        module = importlib.import_module(module_path)
        generatePDFresume = module.generatePDFresume

        generatePDFresume(data, params)
        
        # Open PDF
        os.system(f"open {params['save_path']}")
        print("=== > CV Created Successfully! ____ "+ params['save_path'])

    


# Main function
def main(**kwargs):
    # Provide the shareable link of the google sheet in this format after "gviz/tq?tqx=out:csv&sheet=":
        
    if 'sheet_id' in kwargs:
        sheet_id = kwargs['sheet_id']
    else:
        sheet_id = '1Kkdkra9Yoli7kWrP8TaMRjocRR29Kz2PYxHkYLrUzXo'
    
    print("===== 1/2) GET DATA FROM SHEET ....")
    DFraw , data, params = get_data_from_sheet(sheet_id)
    
    
    print("===== 2/2) GENERATE CV ....")
    generate_cv( data, params )




if __name__ == "__main__":
    main()
