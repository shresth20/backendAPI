from pydantic import BaseModel, AnyUrl, EmailStr, Field, field_validator, model_validator, computed_field 
from typing import List, Dict, Optional, Annotated 

# user data collected by client side
data = {'name': 'Joy',
        'email':'joy2020@sbi.com',
        'file_drive':'https://drive/joy-checkup-files', 
        'age': 20, 
        'weight': 50.5,
        'height': 1.79,  
        'contact_no':{'phone1':'9100202', 'phone2':'8927622'}, }

# Type validation
class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, title='Patient name', description='Enter patient name in 50 chars.', example=['Joy', 'Binod'])] 
    email: Annotated[EmailStr, Field(title='Enter patient email id')]
    file_drive: Annotated[AnyUrl, Field(title='Enter patient checkup files url', description='If patient has had Checkup then Upload all checkup files on Drive then enter share link', default='No Checkup')]
    age: Annotated[int, Field(gt=0, lt=120)]
    weight: Annotated[float, Field(title='Enter patient body weight in Kg', gt=0, strict=True)]
    height: Annotated[float, Field(title='Enter patient body height in Meters', gt=0, strict=True)]
    married: Annotated[Optional[bool], Field(default=False, description='Entre True if patient is married')]  
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]  
    contact_no:Dict[str, str]

    # varify spacific domain mail
    @field_validator('email')
    @classmethod
    def verify_email(cls, value):
        domain= ['hdfc.com', 'sbi.com']
        valid_mail = value.split('@')[-1]
        if valid_mail not in domain:
            raise ValueError('Not a Valid email')
        return valid_mail

    # transform validation
    @field_validator('name')
    @classmethod
    def transform_name(cls, value): 
        return value.upper() 
      
    # model vatidetor access all fields of pydantic model  
    @model_validator(mode='after')
    @classmethod
    def check_emergency_no(cls, model):
        if model.age >=60 and 'emergency' not in model.contact_no:
            raise ValueError('Elder/Old age patient must have Emergency contact no.')
        return model
    
    # create new field with provided data fields 
    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi




# Here patient_type var store correct/valid data which we expacted
patient_type = Patient(**data)

# Inserting data into database
def insert_patient_data(pat: Patient):
    name = pat.name
    age = pat.age 
    weight = pat.weight
    height = pat.height
    file = pat.file_drive
    print(name, age, weight, height,f"BMI is: {pat.bmi}", pat.contact_no, pat.married, ':Data Inserted Successfully')
 
insert_patient_data(patient_type) 