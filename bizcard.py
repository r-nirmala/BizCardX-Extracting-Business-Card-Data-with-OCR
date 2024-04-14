import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import numpy as np
import easyocr
import re
import io
import pandas as pd
import mysql.connector

#---------------------------setting page---------------------------------

st.set_page_config(page_title= "BizCardX",
                   layout= "wide",
                   initial_sidebar_state= "expanded")
def setting_bg():
    image_url = "https://cdn.pixabay.com/photo/2014/01/23/21/37/yellow-250780_1280.jpg"
    st.markdown(f""" <style>.stApp {{
                        background:url("{image_url}");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)


setting_bg()
                                    
st.markdown("<h2 style='text-align: center; color: green;'>BizCardX: Extracting Business Card Data with OCR</h2>",
            unsafe_allow_html=True)
st.write("")
selected = option_menu(None, ["Home", "Upload & Extract",  "View & Modify"], 
                        icons=['house', 'cloud-upload', "pencil"], 
                        menu_icon="cast", default_index=0, orientation="horizontal",
                        styles={"nav-link": {"font-size": "23px", "text-align": "centre", "margin": "-3px",
                                            "--hover-color": "grey"},
                               "icon": {"color":"blue", "font-size": "23px"},
                               "container": {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#ff5757"}})

#-----------------------function for reader setup------------------------
if selected == "Home":
  st.subheader(":violet[Welcome to Business Card Application!] ")
  col1,col2 = st.columns([3.5,3.5],gap="large")
  with col1:   
    Img = Image.open(r"C:\Users\rnirm\OneDrive\Desktop\image\home page_bizcard.jpg")
    size = (590,570)
    Img_1 = Img.resize(size)
    st.image(Img_1)
  with col2:
    st.text('')
    st.text('')
    st.markdown('##### _****:red[Bizcard]****_ is a Python application designed to _extract information_ from business cards and store it in a _****database****_ for further analysis.')
    st.markdown('##### By leveraging the power of _****:blue[OCR (Optical Character Recognition)]****_ provided by _****:green[EasyOCR]****_, Bizcard extracts key details from uploaded business card images such as the _name_, _designation_, _company_, _contact information_, and other relevant data.')         
    st.markdown('##### The card details along with its image stored in the database can be _viewed_, _modified_ or _deleted_.')
    st.write("##### ***Technologies Used:-*** ")
    st.write("##### -->_:orange[Python]_ ")
    st.write("##### -->_:orange[Streamlit]_ ")
    st.write("##### -->_:orange[EasyOCR]_ ")
    st.write("##### -->_:orange[Pandas]_ ")
    st.write("##### -->_:orange[MySQL]_ ")
    st.markdown("##### Click on the ****:red[Upload & Extract]**** tab to start exploring the Bizcard extraction.")

def reader_setup():
    reader = easyocr.Reader(['en'])
    return reader

reader1 = reader_setup()

def extracted_text(texts):  
  card = " ".join(text)
  replacing=[
      (';',""),
      (',',''),
      ('.com','com'),
      ('com','.com'),
      ('WWW ','www.'),
      ("www ", "www."),
      ('www', 'www.'),
      ('www.','www'),
      ('wWW','www'),
      ('wwW','www')]
  for old, new in replacing:
    card = card.replace(old, new)
  
  #-------Extracting phone number------------
  phone_pattern=r"\+*\d{2,3}-\d{3,4}-\d{4}"
  match1=re.findall(phone_pattern,card)
  Phone = ''
  for phone in match1:
      Phone = Phone + '' + phone
      card=card.replace(phone,"")
  
  #--------------Extracting pincode--------------
  pin_code=r"\d+"
  Pincode = ''
  match2=re.findall(pin_code,card)
  for code in match2:
      if len(code)==6 or len(code)==7:
          Pincode=Pincode+code
          card=card.replace(code,"")
  
  #--------------Extracting email id--------------------
  email_id=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}\b"
  Email_id = ''
  match3=re.findall(email_id,card)
  for ids in match3:
      Email_id = Email_id + ids
      card=card.replace(ids,'')
      
  #-----------Extracting web url--------
  web_url=r"www\.[A-Za-z0-9]+\.[A-Za-z]{2,3}"
  Web_Url = ''
  match4=re.findall(web_url,card)
  for url in match4:
      Web_Url = url + Web_Url
      card=card.replace(url,"")
 
  #-----------Extracting alpha words from the result---------------------
  alpha_patterns = r'^[A-Za-z]+ [A-Za-z]+$|^[A-Za-z]+$|^[A-Za-z]+ & [A-Za-z]+$'
  alpha_var=[]
  for i in text:
      if re.findall(alpha_patterns,i):
          if i not in 'WWW':
              alpha_var.append(i)
              card=card.replace(i,"")
  
  dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[],
            "ADDRESS":[], "CITY":[], "STATE":[], "PINCODE":[]}

  dict["NAME"].append(alpha_var[0])
  dict["DESIGNATION"].append(alpha_var[1])
  if len(alpha_var)==3:
      dict["COMPANY_NAME"].append(alpha_var[2])
  else:
      dict["COMPANY_NAME"].append(alpha_var[2]+" "+alpha_var[3])
  dict["CONTACT"].append(Phone)
  dict["EMAIL"].append(Email_id)
  dict["WEBSITE"].append(Web_Url)
  dict["PINCODE"].append(Pincode)
  
  new_card=card.split()
  if new_card[4]=='St':
    dict["CITY"].append(new_card[2])
  else:
    dict["CITY"].append(new_card[3])
  
  if new_card[4]=="St":
    dict["STATE"].append(new_card[3])
  else:
    dict["STATE"].append(new_card[4])
  
  if new_card[4]=='St':
    dict["ADDRESS"].append(new_card[0]+" "+new_card[1]+" "+new_card[4])
  else:
    dict["ADDRESS"].append(new_card[0]+" "+new_card[1]+" "+new_card[2])
  return dict

#--------------------------mysql connection------------------------------
con = mysql.connector.connect(host = "localhost", user= "root", password = "12345")
mycursor = con.cursor()
mycursor.execute('create database if not exists bizcard')
mycursor.execute('use bizcard')

#------------------------------upload & extract----------------------------
if selected ==  "Upload & Extract":  
  image = st.file_uploader(label = "Upload image", type =['png','jpg','jpeg'], label_visibility="hidden")
  if image is not None:
    input_image = Image.open(image)
    col1, col2 = st.columns([3.5,3.5],gap="small")
    with col1:
        st.image(input_image, width=500, caption='Uploaded Image')   
    with col2:
        text = reader1.readtext(np.array(input_image), detail=0)
        st.write(text)
    dict = extracted_text(text)
    df = pd.DataFrame(dict)
        
    #image to binary
    image_bytes = io.BytesIO()
    input_image.save(image_bytes, format='PNG')
    image_data = image_bytes.getvalue()
    
    # Creating dictionary
    data = {"Image": [image_data]}
    df_1 = pd.DataFrame(data)
    concat_df = pd.concat([df,df_1],axis =1)
    st.write(concat_df)
    
    st.write("##### :violet[Click the button below to upload the business card details into the Database]")
    submit = st.button("### :orange[Upload to database]")
    if submit:
      with st.spinner('In Progress..'):
             
        #sql connection
        con = mysql.connector.connect(host = "localhost", user= "root", password = "12345", database="bizcard")
        mycursor = con.cursor()
        
        #create table  
        try:
          create_query = '''create table if not exists card_details (Name varchar(100) primary key, 
                                                        Designation varchar(100),
                                                        Company_Name varchar(100),
                                                        Contact varchar(100),
                                                        E_mail varchar(100),
                                                        Website varchar(100),
                                                        Address varchar(100),
                                                        City varchar(100),
                                                        State varchar(100),
                                                        Pincode varchar(100),
                                                        Image LONGBLOB)'''
          mycursor.execute(create_query)
          con.commit()

          #insert values to table
          insert_query = ''' insert into card_details (Name, Designation, Company_Name, 
                                Contact, E_mail, Website, Address, City, State, Pincode,Image)
                                  
                                  values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) '''
          data = concat_df.values.tolist()[0]
          mycursor.execute(insert_query,data)
          con.commit()
          st.success('###### :rainbow[Uploaded successfully]',icon="✅")
        except:
          st.error("##### :red[Card Details of this person are already uploaded]")
  else:
    st.write("##### :green[Upload an image]")

#---------------------Modify----------------------
if selected == "View & Modify":
  opt = st.radio("###### :orange[Select any option]",['***Database***','***View Card***','***Update data***','***Delete data***'],horizontal = True)
  if opt == '***Database***':
    st.write('###### :violet[You selected to view the]',opt)
    mycursor.execute('select * from card_details')
    df = pd.DataFrame(mycursor.fetchall(), columns = mycursor.column_names)
    st.write(df)
 
  elif opt == '***View Card***':
    col1, col2 = st.columns([3.5,3.5],gap="medium")
    with col1:
      mycursor.execute("select Name from card_details")
      rows = mycursor.fetchall()
      name = [row[0] for row in rows]

      selected_name = st.selectbox("###### :violet[Select the Name]",name)
      if st.button("### :green[Display Card]"):
        with st.spinner('Please wait for it...'):
          with col2:
            sql = "select Image from card_details where Name = %s"
            mycursor.execute(sql,(selected_name,))
            result = mycursor.fetchone()

            if result is not None:
              byte_data = result[0]
              image = io.BytesIO(byte_data)
              f_img = Image.open(image)
              st.image(f_img, width =500)
            else:
              st.error("###### :red[Image not found for the given Name]")

  elif opt == '***Update data***':
    col1, col2 = st.columns([3.5,3.5],gap = "medium")
    with col1:
      mycursor.execute("select Name from card_details")
      rows = mycursor.fetchall()
      name = [row[0] for row in rows]

      selected_name = st.selectbox("###### :blue[Select Card holder Name for Updation]",name)
      mycursor.execute('show columns from card_details')
      columns = mycursor.fetchall()
      column_names = [i[0] for i in columns if i[0] not in ['Id', 'Image']]

      ch = st.selectbox("###### :blue[Select the column to update]", column_names)
      new_data = st.text_input(f"###### Enter the new {ch} to update")
      if st.button ("### :red[UPDATE]"):
        with st.spinner('Updation In Progress...'):
          sql = f'UPDATE card_details SET {ch} =%s WHERE Name = %s'
          mycursor.execute(sql,(new_data,selected_name))
          con.commit()
          if mycursor.rowcount>0:
            st.success("##### :red[Updated successfully]",icon ="✅")
          else:
            st.error("###### :violet[Please choose the correct name to update]")
    with col2:
      st.write("##### :green[The changes made to the Database are shown here.]")
      mycursor.execute('select * from card_details')
      updated_data = mycursor.fetchall()
      df = pd.DataFrame(updated_data, columns=mycursor.column_names)
      st.dataframe(df)

  elif opt == '***Delete data***':
    col1, col2 = st.columns([3.5,3.5],gap="medium")
    with col1:
      mycursor.execute("select Name from card_details")
      rows = mycursor.fetchall()
      name = [row[0] for row in rows]
      selected_name = st.selectbox("###### :violet[Select Card holder Name to Delete from Database]",name)

      if st.button("### :green[DELETE]"):
        with st.spinner('Deletion In Progress...'):
          sql = "DELETE from card_details WHERE Name = %s"
          mycursor.execute(sql,(selected_name,))
          con.commit()
          if mycursor.rowcount>0:
            st.warning('##### :red[DELETED]', icon="⚠️")
          else:
            st.error("###### :blue[Please choose the correct name to delete]")

    with col2:
      st.write("##### :green[The changes made to the Database are shown here.]")
      mycursor.execute('select * from card_details')
      updated_data = mycursor.fetchall()
      df = pd.DataFrame(updated_data, columns=mycursor.column_names)
      st.dataframe(df)
