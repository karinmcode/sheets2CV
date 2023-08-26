# Google Sheet CV Generator

This Python script is designed to help users fetch CV (Curriculum Vitae) data from a Google Sheet and generate a PDF version of the CV using the ReportLab Python library.

## How it works:

1. **Fetching Data from Google Sheet**: The code fetches CV data from a Google Sheet, converting the Google Sheet into a pandas DataFrame. The user can provide a Google Sheet ID as an argument, or a default ID is used if not provided.

2. **Data Formatting**: Once the CV data is fetched, the script formats it, segregating various sections like Personal Details, Education, Professional Experience, Skills, etc.

3. **Populating the CV**: Using the ReportLab library, the script populates the CV data into a PDF format, as per the template provided in the Google Sheet.

## Main Components:

1. **get_data_from_sheet(sheet_id)**: 
    - Retrieves data from two sheets: `data` and `params`.
    - The `data` sheet contains CV details, while `params` contains parameters for generating the CV.
    
2. **getParams(sheet_url)**: 
    - Extracts the parameters needed for generating the CV.

3. **formatData(DF)**:
    - Formats the fetched data and organizes it into various sections.

4. **generate_cv(data, PARAMS)**:
    - Calls a function to create the PDF using the ReportLab library.
    - Opens the generated PDF.

5. **main(sheet_id)**:
    - Executes the process by fetching the data and then generating the CV.

## Usage:

To use this script, follow these steps:

1. **Google Sheet Preparation**: 
    - Ensure you have a Google Sheet prepared with all the CV data. The Google Sheet should have two sheets named `data` and `params`. 
    - The `data` sheet should have your CV details and the `params` sheet should have parameters for generating the CV such as template_name, pdf_name, etc.
    - Make sure to set your Google Sheet permissions to 'Anyone with the link can view'.

2. **Environment Setup**:
    - Make sure you have Python 3 installed.
    - Install necessary libraries: `pip install pandas reportlab`.

3. **Executing the Script**:
    - Run the script in your terminal or command prompt.
    - If you wish to provide your Google Sheet ID, run it like this: `python <script_name>.py --sheet_id YOUR_GOOGLE_SHEET_ID`
    
4. **Output**:
    - Once the script runs successfully, a PDF CV will be generated in the location specified in the `params` sheet.

5. **Customizing the PDF Template**:
    - The `params` sheet allows you to specify a template name. You can create different python files (templates) to define different styles of CVs.

## Note:

Make sure the Google Sheet is accessible and properly formatted to match the requirements of the script. Always check if the necessary permissions are set and the sheet structure matches what the script expects.
