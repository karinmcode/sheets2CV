#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# """
# Created on Tue Aug 25 14:08:21 2023

# @author: karinmorandell
#"""

import mylib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm

from reportlab.platypus import Image as ReportLabImage # for logos
from reportlab.lib.enums import TA_LEFT

from PIL import Image as piImage

import os

WIDTH, HEIGHT = A4


#from reportlab.pdfgen import canvas # for langage level 'health gauge"
# from reportlab.platypus import Flowable # for langage level 'health gauge"
from reportlab.platypus.flowables import Flowable

import re

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# Register the font files (assuming they are in a 'fonts' directory relative to your script)
# List all font files in the fonts directory
font_files = [f for f in os.listdir("fonts/") if f.endswith(".ttf")]

# Register each font
for font_file in font_files:
    font_name = os.path.splitext(font_file)[0]  # Extract the font name without extension
    pdfmetrics.registerFont(TTFont(font_name, os.path.join("fonts", font_file)))


global params
################################################################################################
################################################################################################
###### FUNCTIONS
################################################################################################
################################################################################################



def checkParams(params):
    ################################################################################################
    ################################################################################################
    ###### MAIN STYLING VARIABLES
    ################################################################################################
    ################################################################################################
    
    default_params = {
        'gray_level':       0.4,
        'color':            colors.Color(0.5, 0.1, 0.1) ,
        'fontname':         'calibri',
        'fontname_headers': 'calibri_bold',
        }
    
    # check if params has those fields defined
    
    for key in default_params:
        
        if key not in params:
            params[key] = default_params[key]
            
        if key == 'color':
            # check that is well defined
            if params['color'][0]=='#':
                HEX = params['color']
                RGB = mylib.hex2rgb(HEX)
                params['color'] = colors.Color(RGB[0],RGB[1],RGB[2])
            
    c = params['color']   
    params['color_hex'] = c.hexval()
    g = params['gray_level']
    params['color_grey'] = colors.Color(g, g, g)
    g = params['color_grey']
    params['color_grey_hex'] = params['color_grey'].hexval()

    return params

class HealthBar(Flowable):
    # init function
    def __init__(self, width, height, color, level):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color
        self.level = level
        
    def draw(self):

        # Draw the filled segment of the bar with rounded corners
        bar_width = self.width * self.level
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, bar_width, self.height, self.height / 2, stroke=0, fill=1)
        
        # If bar isn't full, overlay a white or colored rectangle to cover the right rounded corner of the filled segment
        if self.level < 1:
            self.canv.setFillColor(self.color)
            #self.canv.rect(bar_width - self.height / 2, 0, self.height / 2, self.height, fill=1, stroke=0)
            x = bar_width 
            y = 0
            w = -self.height / 3
            h = self.height
            self.canv.rect(x , y, w,h , fill=1, stroke=0)
        elif self.level <0.3:
            self.canv.setFillColor(colors.Color(255, 255, 255))
            #self.canv.rect(bar_width - self.height / 2, 0, self.height / 2, self.height, fill=1, stroke=0)
            x = bar_width - self.height / 3 
            y = 0
            w = self.height / 2
            h = self.height
            self.canv.rect(x , y, w,h , fill=1, stroke=0)            
            
        # Draw a full-width rounded rectangle as background
        self.canv.setLineWidth(0.5)  # Set the line thickness to 2 points
        self.canv.setStrokeColor(colors.Color(0, 0, 0))  # Set outline color to black
        self.canv.roundRect(0, 0, self.width, self.height, self.height / 2, stroke=1, fill=0)


def addHeaBarList(obj,list2split,params,**kwargs):
    
    
    if 'width' in kwargs:
        total_width = kwargs['width']
    else:
        total_width = 6*cm
        
    if 'style' in kwargs:
        style = kwargs['style']
    else:
        styles = getSampleStyleSheet()

        style = ParagraphStyle(
            name='healthbarlist',
            parent=styles['Normal'],  # Start with an existing style
            fontSize=10,
            textColor="Black",
            fontName=params['fontname'],
        )     
        
        
    icon_width = 0.8*cm
    text_width = total_width-icon_width
    
    Healthbar_Table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, -1), 0.02*cm),
        ('LEFTPADDING', (-1, 0), (-1, -1), -0.01*cm),
        ('TOPPADDING', (-1, 0), (-1, -1), -0.05*cm),
        ] )
    
    
    TableArray = []
    
    for index,item in enumerate(list2split.split(';')):

        text = re.split('<', item)[0]
        thisLevel= float(re.findall('<([0-9\.]*)>', item)[0])
        hb=HealthBar(width=0.5*cm,height=0.15*cm,color=params['color_hex'],level=thisLevel)
        
        p = Paragraph(text,style)
        TableArray.append([hb, p])
    

    
    # Generate row heights using numpy's broadcasting    
    langageTable = Table(TableArray, colWidths=[icon_width, text_width])
    langageTable.setStyle(Healthbar_Table_style)
    obj.append(langageTable)
    
    
    return obj


class HorizontalLine(Flowable):
    # init function
    def __init__(self, width, color):
        Flowable.__init__(self)
        self.width = width
        self.color = color

    # drawing the line
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.line(0, 0, self.width, 0)


def addEvent(elements,date1,date2,position,location,params,**kwargs):
    
        
    col_width1 = 2.8
    col_width2 = 9.5

    # Make styles for each part of the event:
    #  t1-t2   | position     
    #          | location
    # Load default sample styles
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = params['fontname']
    
            
    # Dates Style
    styles.add(ParagraphStyle(
        name='dates',
        parent=styles['Normal'],
        fontSize=10,
        fontName='calibri_light',
        textColor=colors.Color(params['gray_level'], params['gray_level'], params['gray_level']),
        italic=True,
    ))
    
    # Location Style
    styles.add(ParagraphStyle(
        name='location',
        parent=styles['Normal'],
        fontSize=10,
        fontName='calibri_light',
        textColor=colors.Color(params['gray_level'], params['gray_level'], params['gray_level']),
    ))
    
    # Position Style
    styles.add(ParagraphStyle(
        name='position',
        parent=styles['Normal'],
        fontSize=11,
        fontName='calibri_bold',
        bold=True,
    ))
    
    # Description Style
    styles.add(ParagraphStyle(
        name='description',
        parent=styles['Normal'],
        fontSize=10,
        fontName='calibri',
        textColor='Black',
    ))
    
    # Publications Style
    styles.add(ParagraphStyle(
        name='publications',
        parent=styles['Normal'],
        fontSize=8,
        italic=True,
        textColor=colors.Color(params['gray_level'], params['gray_level'], params['gray_level']),
        fontName='calibri_light',
    ))
 
        
    ## MAKE DATE TABLE
    dates = str(round(date1))+'-'+str(round(date2))
    logo = changeLogo("icons/calendar.png",params['gray_level'])
    

    
    
    date_table = Table([[logo, Paragraph('  '+dates, styles['dates'])]], colWidths=[0.45*cm, (col_width1-0.45)*cm])
    
    # Apply some styling if needed (like padding, borders etc.)
    t_date_style = TableStyle([
        ('VALIGN',          (0, 0), (-1, -1),   'MIDDLE'),
        ('LEFTPADDING',     (0, 0), (-1, -1),   0*cm), # all cells
        ('LEFTPADDING',     (0, 0), (0, 0),      -0.01*cm), # text cells
        ('LEFTPADDING',     (-1, -1),(-1,-1),   0.1*cm), # text cells
        ('TOPPADDING',      (0, 0), (-1, -1),   0),     # all cells
        ('BOTTOMPADDING',   (0, 0), (-1, -1),   0), # all cells
    ])        
    
    date_table.setStyle(t_date_style)
    
    ## MAKE LOCATION TABLE
    
    logo = changeLogo("icons/location.png",params['gray_level'])
    
    location_table = Table([[logo, Paragraph('  '+location, styles['location'])]], colWidths=[0.5*cm, 9*cm])
    
    loc_tab_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), -0.1*cm),
        ('TOPPADDING', (0, 0), (-1, -1), -0.5*cm),     
        ('BOTTOMPADDING', (0, 0), (-1, -1), -0.5*cm),                   
    ])

    location_table.setStyle(loc_tab_style)
    
    p = Paragraph(position ,  styles['position'] )
    
    event_table = Table(
        [   [p,'']  ,   [date_table,location_table] ],
        colWidths=[col_width1*cm,col_width2*cm]
        )
    
    TABLE_STYLE = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (0, -1), -0.03*cm),     # first column, all rows
        ('TOPPADDING', (0, -1), (-1, -1), -0.1*cm),    # last row : location
        ('BOTTOMPADDING', (0, -1), (-1, -1), -0.02*cm),    # last row  : location
        ('SPAN',            (0,0),(1,0))
        
    ])        
    
    event_table.setStyle(TABLE_STYLE)
    elements.append(event_table)
    
    
    # add descriptions and publications
    table_data = []
    
    if 'descriptions' in kwargs:
        descriptions = kwargs['descriptions']
        
        ndes = len(descriptions)
        if ndes !=0:
            for ides in range(0,ndes):
                d = descriptions[ides]
                
                d = d.replace('Project:','<b>Project:</b>')
                d = d.replace('Skills:','<b>Skills:</b>')

                d = d.replace('Project:','• Project:')
                d = d.replace('Skills:','• Skills:')

                table_data.append(Paragraph(d,styles['description']))            
    
        
    
    
    if 'publications' in kwargs:
        publications = kwargs['publications']

        pub_tab_style = TableStyle([
            ('VALIGN', (-1, -1), (-1, -1), 'BOTTOM'),   # text position     
            
            ('TOPPADDING',      (0, 0), (0, 0),     0*cm),# icon position
            ('BOTTOMPADDING',   (0, 0), (0, 0),     0*cm),# icon position
            
            ('TOPPADDING',      (-1, -1), (-1, -1), 0*cm),# text position
            ('BOTTOMPADDING',   (-1, -1), (-1, -1), -0.05*cm),   # text position
                        
            
        ])        

        logo = changeLogo("icons/publication.png", params['gray_level'])

        npub = len(publications)
        if npub !=0:
            for ipub in range(0,npub):
                pub = publications[ipub]['text']
                url = publications[ipub]['url']
                text = f'<link href="{url}">{pub}</link>'
                p = Paragraph(text,styles['publications'])
                pub_table = Table([[logo, p]], colWidths=[0.5*cm, 9*cm])
                pub_table.setStyle(pub_tab_style)
                table_data.append(pub_table)
            
    if len(table_data)!=0:        
        EXP_TABLE = Table(
            [[table_data,'' ]],
            colWidths=[col_width1*cm,col_width2*cm]
        )
        
        table_style = TableStyle([
            ('LEFTPADDING', (1, 0), (1, 0), -0.2*cm),
            ('SPAN',            (0,0),(-1,0))
            
            
            
        ])       
        
        EXP_TABLE.setStyle(table_style)
        
        elements.append(EXP_TABLE)
    
    return elements

       
def addSection(elements,text,width,section_color,fontname_headers,spacer_offset):
    
    styles = getSampleStyleSheet()
    
    if isinstance(section_color,colors.Color) : #type(section_color)
        section_color = section_color.hexval()
        
    # Section Style
    styles.add(ParagraphStyle(
        name='section',
        parent=styles['Heading3'],  # Start with an existing style
        textColor=section_color,
        fontSize=12,
        fontName=fontname_headers,
        italic=False,
        bold=True,
    ))

    
    elements.append(Paragraph(text.upper(), styles['section']))
    # Add a horizontal line separator
    elements.append(HorizontalLine(width=width, color=section_color))
    elements.append(Spacer(1, spacer_offset*cm))
    
    return elements        
    

def changeLogo(url,alpha):

    a = round(alpha*10)
    new_url = url.replace('.png',f'_alpha{a}.png')
    
    if os.path.isfile(new_url):
        # Create a ReportLabImage instance with the specified image URL and mask
        im = ReportLabImage(new_url, width=0.4*cm, height=0.4*cm)
    else:
        im = piImage.open(url)
    
        # Convert the image to RGBA mode
        im = im.convert("RGBA")
    
        # Get the pixel data as a list of tuples
        pixel_data = list(im.getdata())
        
        # Replace pixel values below 10 with alpha
        alpha = round(255*alpha)
        modified_pixel_data = [(alpha, alpha, alpha, pixel[3]) if all(val < 50 for val in pixel[:3]) else pixel for pixel in pixel_data]
        
        # Create a new image with the modified pixel data
        modified_im = piImage.new("RGBA", im.size)
        modified_im.putdata(modified_pixel_data)
        
        modified_im.save(new_url)
    
        # Create a ReportLabImage instance with the specified image URL and mask
        im = ReportLabImage(new_url, width=0.4*cm, height=0.4*cm)

    return im


def getCustomStyles(params):
    
    # Load default sample styles
    styles = getSampleStyleSheet()
        
    styles['Normal'].fontName = params['fontname']
    

    
    # Name Style
    styles.add(ParagraphStyle(
        name='name',
        parent=styles['Heading1'],  # Start with an existing style
        fontSize=28,
        fontName=params['fontname_headers'],
        bold=True,
        textColor=params['color_hex'],
    ))
    
    # Subheader Style
    styles.add(ParagraphStyle(
        name='subheader',
        parent=styles['Heading2'],  # Start with an existing style
        fontSize=14,
        fontName='calibri',
        textColor=params['color_grey_hex'],  # Assuming params['color_grey_hex'] is defined elsewhere
    ))

    
    # Contact Style
    styles.add(ParagraphStyle(
    name='contact',
    parent=styles['Normal'],  # Start with an existing style
    fontName = 'calibri_light',
    textColor=params['color_grey_hex'],  # Assuming params['color_grey_hex'] is defined elsewhere
    fontSize=10,              # Change font size
    )) 

        
    # Info Style
    styles.add(ParagraphStyle(
        name='info',
        parent=styles['Normal'],  # Start with an existing style
        fontName=params['fontname'],
        alignment=4,  # justified
        textColor="Black",
        fontSize=10,
    ))
    
    # Section Style
    styles.add(ParagraphStyle(
        name='section',
        parent=styles['Heading3'],  # Start with an existing style
        textColor=params['color_hex'],
        fontSize=14,
        fontName=params['fontname_headers'],
        italic=False,
        bold=True,
    ))
    
    

    # strengths Style
    styles.add(ParagraphStyle(
        name='strengths',
        parent=styles['Normal'],  # Start with an existing style
        fontSize=11,
        textColor=params['color_hex'],
        fontName=params['fontname'],
        alignment = 0,
    ))
    
    # Data Style
    styles.add(ParagraphStyle(
        name='data',
        parent=styles['Normal'],  # Start with an existing style
        fontSize=10,
        fontName=params['fontname'],
        alignment=4,  # justified
        textColor="Black",
    ))
    
    # Skill Style
    styles.add(ParagraphStyle(
        name='skill',
        parent=styles['Normal'],  # Start with an existing style
        fontSize=11,
        textColor="Black",
        fontName=params['fontname'],
    ))

    
    # Subsection Style (which is same as skill_style)
    styles.add(ParagraphStyle(
        name='subsection',
        parent=styles['skill'],  # Start with an existing style
    ))    
    
    return styles

def generatePDFresume(data, params):

    
    params = checkParams(params)
    
    styles = getCustomStyles(params)
    
    ################################################################################################
    ################################################################################################
    #### CUSTOM PARAGRAPH STYLES AND COLORS
    ################################################################################################
    ################################################################################################


    # Define columns widths
    W1 = 0.6
    W2 = 0.2
    spacer_offset = 0.25
    line_width1 = W1*WIDTH-1.2*cm
    line_width2 = W2*WIDTH-0.5*cm
        
    ################################################################################################
    ################################################################################################
    ###### UNPACK DATA
    ################################################################################################
    ################################################################################################
    
    # unpack data
    contact = data['contact']
    experience = data['experience']
    education =data['education']
    key_skills= data['key_skills']
    skills = data['skills']
    tech_skills= data['tech_skills']
    langages = data['langages']
    about_me = data['about_me']

    # Create a PDF document with A4 paper size
    doc = SimpleDocTemplate(params['save_path'],
                            pagesize=A4,
                            unit=cm,
                            bottomMargin=1*cm,
                            topMargin=1*cm,
                            rightMargin=1*cm,
                            leftMargin=1*cm)  # set the doc template

    ################################################################################################
    ################################################################################################
    #### HEADER AND CONTACT
    ################################################################################################
    ################################################################################################

    ################################################################################################
    #### - LEFT_COLUMN
    ################################################################################################


    # Create a list to hold elements
    LEFT_COLUMN = [
        Paragraph(contact['name'].upper(), styles['name']),
        Paragraph(contact['title'], styles['subheader'])
    ]

    ################################################################################################
    #### - RIGHT_COLUMN
    ################################################################################################

    # Add the rest of the personal information in the right column
    RIGHT_COLUMN = []
    for key, value in contact.items():
        if key not in ['name', 'title']:
            icon = ''
            text = ''
            if key in ['mobile' , 'address' ,'email','nationality']:
                url = f"icons/{key}.png"
                logo = changeLogo(url,params['gray_level'])
                
                #logo = ReportLabImage(im, width=0.4*cm, height=0.4*cm)             

            elif key == 'linkedin':
                url = f"icons/{key}.png"
                
                logo = changeLogo(url,params['gray_level'])
                
                #logo = ReportLabImage(im, width=0.4*cm, height=0.4*cm)
                text = value.replace('https://www.linkedin.com/in/','')
                text = f'<link href="{value}">{text}</link>'
            elif key == 'github':
                url = f"icons/{key}.png"
                
                logo = changeLogo(url,params['gray_level'])
                
                #logo = ReportLabImage(im, width=0.4*cm, height=0.4*cm)
                text = value.replace('https://github.com/','')
                text = f'<link href="{value}">{text}</link>'


            if icon == '': # if no unicode defined, use image.png for the icons folder and put it in table
                

                if text == '':# if  no link in this row , use image.png for the icons folder
                    
                # Create a table with one row for the logo and text
                    logo_text_table = Table([[logo, Paragraph(' '+value, styles['contact'])]], colWidths=[0.4*cm, 6*cm])
                else:
                    logo_text_table = Table([[logo, Paragraph(' '+text, styles['contact'])]], colWidths=[0.4*cm, 6*cm])
                
                # Apply some styling if needed (like padding, borders etc.)
                table_style = TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                    ('TOPPADDING', (0, 0), (-1, -1), .01),     
                    ('BOTTOMPADDING', (0, 0), (-1, -1), .01),
                ])
                logo_text_table.setStyle(table_style)
                
                RIGHT_COLUMN.append(logo_text_table)
                                
            else: # if  unicode defined in icon 
                info_paragraph = Paragraph(f"{icon} {value}", styles['contact'])
                RIGHT_COLUMN.append(info_paragraph)

    # Add Name and Title in big font on the left column
    CONTACT_TABLE = Table(
        [[LEFT_COLUMN, RIGHT_COLUMN]],
        colWidths=[W1*WIDTH, W2*WIDTH]
    )

    # In ReportLab's table style commands, the first number is the column index and the second number is the row index. 
    CONTACT_TABLE.setStyle(TableStyle([
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),# Vertically align top for left cell
    ('LEFTPADDING', (1, 0), (1, 0), -1.0*cm),
    ('TEXTCOLOR', (-1, -1), (-1, -1), params['color_grey']),
    ]))

    elements = []
    elements.append(CONTACT_TABLE)



    # Spacer between sections
    elements.append(Spacer(1, 0.5*cm))

    ################################################################################################
    ################################################################################################
    #### BODY
    ################################################################################################
    ################################################################################################


    ################################################################################################
    ################################################################################################
    #### - LEFT COLUMN
    ################################################################################################
    ################################################################################################
    LEFT_COLUMN = []


    ################################################################################################
    #### ***** KEY SKILLS
    ################################################################################################
    
    LEFT_COLUMN = addSection(LEFT_COLUMN,'STRENGTHS',line_width1,params['color'],params['fontname_headers'],spacer_offset)

    
    
    nk = len(key_skills)
    for i in range(1,nk+1):
        
        skill= key_skills[i-1]['skill'].upper()
        description = key_skills[i-1]['description']
        text = '<font color="{}">{}</font> '.format(params['color_hex'], skill)
                                
        LEFT_COLUMN.append(Paragraph(text,  styles['strengths']))
        LEFT_COLUMN.append(Paragraph(description,  styles['data']))
        LEFT_COLUMN.append(Spacer(1, 0.3*cm))

    ################################################################################################
    #### EXPERIENCE
    ################################################################################################
    
    LEFT_COLUMN = addSection(LEFT_COLUMN,'Experience',line_width1,params['color_hex'],params['fontname_headers'],spacer_offset)




    nexp = len(experience)
    #####
    # add experiences
    for iexp in range(1,nexp+1):
        e = experience[iexp-1]
        date1 = e['datestart']
        date2 = e['dateend']
        company = e['company']
        location = e['location'] +' ('+ company +')' 
        position = '<b>'+e['position']+'</b>'
        
        LEFT_COLUMN = addEvent(LEFT_COLUMN,date1,date2,position,location,params,descriptions=e['descriptions'],publications=e['publications'] )
        
        


    ################################################################################################
    #### EDUCATION
    ################################################################################################
    LEFT_COLUMN = addSection(LEFT_COLUMN,'Education',line_width1,params['color'],params['fontname_headers'],spacer_offset)
   
    
    nedu = len(education)
    for i in range(1,nedu+1):
        location = education.loc[i-1, 'location']
        position = '<b>'+education.loc[i-1, 'fieldvalue']+'</b>'
        date1 = education.loc[i-1, 'datestart']
        date2 = education.loc[i-1, 'dateend']
        LEFT_COLUMN = addEvent(LEFT_COLUMN,date1,date2,position,location,params)

    ################################################################################################
    ################################################################################################
    #### - RIGHT COLUMN
    ################################################################################################
    ################################################################################################

    RIGHT_COLUMN = []
    
    ################################################################################################
    #### SKILLS
    ################################################################################################
    RIGHT_COLUMN = addSection(RIGHT_COLUMN,'Skills',line_width2,params['color'],params['fontname_headers'],spacer_offset)

    
    skills_list = skills.split(',')
    
    # Bullet point style
    bullet_style = ParagraphStyle('bulletStyle', parent=styles['Normal'], 
                                  bulletFontName='Calibri', bulletFontSize=12, bulletIndent=0, alignment=TA_LEFT)


    bullet_elements = [Paragraph("• " + item, style=bullet_style) for item in skills_list]

    RIGHT_COLUMN.extend(bullet_elements)
    
    ################################################################################################
    #### TECH LANGUAGES
    ################################################################################################
    RIGHT_COLUMN = addSection(RIGHT_COLUMN,'Tech languages',line_width2,params['color'],params['fontname_headers'],spacer_offset)


    doBULLETPOINTS = False
    if doBULLETPOINTS:
        bullet_elements = []
        bullet_elements = [Paragraph("• " + item, style=bullet_style) for item in tech_skills.split(';')]
        
        RIGHT_COLUMN.extend(bullet_elements)
    else:
        
        RIGHT_COLUMN = addHeaBarList(RIGHT_COLUMN,tech_skills,params,width=4*cm)
        


    ################################################################################################
    #### LANGAGES
    ################################################################################################
    RIGHT_COLUMN = addSection(RIGHT_COLUMN,'Langages',line_width2,params['color'],params['fontname_headers'],spacer_offset)
    doBULLETPOINTS = False
    if doBULLETPOINTS:
        bullet_elements = []
        bullet_elements = [Paragraph("• " + item, style=bullet_style) for item in langages.split(';')]
        RIGHT_COLUMN.extend(bullet_elements)
    else:
        
        RIGHT_COLUMN = addHeaBarList(RIGHT_COLUMN,langages, params,width=4*cm)



    

    ################################################################################################
    #### ABOUT ME
    ################################################################################################
    
 

    
    RIGHT_COLUMN = addSection(RIGHT_COLUMN,'About me',line_width2,params['color'],params['fontname_headers'],spacer_offset)   
    
    FORMATING = 'bullets'
    
    if FORMATING == 'bullets':
        
        title_text = '<font color="{}">PERSONALITY</font>'.format(params['color_hex'])
        RIGHT_COLUMN.append(Paragraph(title_text,  styles['subsection']))
        bullet_elements = []
        bullet_elements = [Paragraph("• " + item, style=bullet_style) for item in about_me['personality'].split(',')]
        RIGHT_COLUMN.extend(bullet_elements)
        
        RIGHT_COLUMN.append(Spacer(1, 0.8*spacer_offset*cm))      
        
        title_text = '<font color="{}">INTERESTS</font>'.format(params['color_hex'])
        RIGHT_COLUMN.append(Paragraph(title_text,  styles['subsection']))
        bullet_elements = []
        bullet_elements = [Paragraph("• " + item, style=bullet_style) for item in about_me['interests'].split(',')]
        RIGHT_COLUMN.extend(bullet_elements)        
        
    else:
        # Create the paragraphs with new lines after titles
        personality_text = '<font color="{}">PERSONALITY</font><br/> {}'.format(params['color_hex'], about_me['personality'])
        interests_text = '<font color="{}">INTERESTS</font><br/> {}'.format(params['color_hex'], about_me['interests'])

        
        RIGHT_COLUMN.append(Paragraph(personality_text,  styles['subsection']))
        RIGHT_COLUMN.append(Spacer(1, 0.5*spacer_offset*cm))      
        RIGHT_COLUMN.append(Paragraph(interests_text, styles['subsection']))


    ################################################################################################
    ################################################################################################
    ###### FINALIZE THE LAYOUT WITH BOTH COLUMNS
    ################################################################################################
    ################################################################################################
    section_table = Table(
        [[LEFT_COLUMN, RIGHT_COLUMN]], colWidths=[W1*WIDTH, W2*WIDTH])

    # Apply some styling if needed (like padding, borders etc.)
    table_style = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('RIGHTPADDING', (0, 0), (0, 0), 1*cm),
        ])
    section_table.setStyle(table_style)
    
    elements.append(section_table)

    # Build the PDF document
    doc.build(elements)



