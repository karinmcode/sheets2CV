# Google Sheet CV Generator : sheets2CV

This Python script is designed to help users fetch CV (Curriculum Vitae) data from a Google Sheet and generate a PDF version of the CV using the ReportLab Python library.

<div align="center">
    <img src="https://github.com/karinmcode/sheets2CV/blob/main/icons/example_CV.png?raw=true" width="900">
</div>

## How it works:

1. **Fetching Data from Google Sheet**: The code fetches CV data from a Google Sheet, converting the Google Sheet into a pandas DataFrame. The user can provide a Google Sheet ID as an argument, or a default ID is used if not provided.

2. **Data Formatting**: Once the CV data is fetched, the script formats it, segregating various sections like Personal Details, Education, Professional Experience, Skills, etc.

3. **Populating the CV**: Using the ReportLab library, the script populates the CV data into a PDF format, as per the template provided in the Google Sheet.


## Usage:

To use this tool, follow the steps on this [Google Colab](https://colab.research.google.com/drive/1TlZdNDkT2mwvZ8epSRwe8B-JO7R1N5z9#scrollTo=QpOVmbUjR8De).

## Note:

Make sure the Google Sheet is accessible and properly formatted to match the requirements of the script. Always check if the necessary permissions are set and the sheet structure matches what the script expects.
