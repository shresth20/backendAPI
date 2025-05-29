from pydantic import BaseModel, AnyUrl, EmailStr, Field, field_validator, model_validator, computed_field, constr 
from typing import List, Dict, Optional, Annotated 

# user data collected by client side
data = {'name': 'Joy',
        'email':'joy2020@sbi.com',
        'file_drive':'https://drive/joy-checkup-files', 
        'age': 20, 
        'weight': 50.5,
        'height': 1.79,  
        'contact_no':{'phone1':'9100202', 'phone2':'8927622'}, 
        'address': {'city':'lucknow', 'pincode': 226001, 'state':'uttar paradesh'}}


# nested model- if we use a model as field in other model 
class Address(BaseModel):
    city: Annotated[str, Field(max_length=20)]
    pincode: Annotated[int, constr(strict=True, min_length=6, max_length=6)]
    state: Annotated[str, Field(max_length=20)]

# Data Type validation
class Patient(BaseModel):
    name: Annotated[str, Field(max_length=50, title='Patient name', description='Enter patient name in 50 chars.', example=['Joy', 'Binod'])] 
    email: Annotated[EmailStr, Field(title='Enter patient email id')]
    file_drive: Annotated[AnyUrl, Field(title='Enter patient checkup files url', description='If patient has had Checkup then Upload all checkup files on Drive then enter share link', default='No Checkup')]
    age: Annotated[int, Field(gt=0, lt=120)]
    weight: Annotated[float, Field(title='Enter patient body weight in Kg', gt=0, strict=True)]
    height: Annotated[float, Field(title='Enter patient body height in Meters', gt=0, strict=True)]
    married: Annotated[Optional[bool], Field(default=False, description='Entre True if patient is married')]  
    allergies: Annotated[Optional[List[str]], Field(default=None, max_length=5)]  
    contact_no: Dict[str, str]
    # address use as nested model
    address: Annotated[Address, Field(title='Enter patient address')]

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
    

# Inserting data into database
def insert_patient_data(pat: Patient):
    name = pat.name
    age = pat.age 
    weight = pat.weight
    height = pat.height
    file = pat.file_drive
    bmi = f"BMI is: {pat.bmi}"
    contact =pat.contact_no
    married = pat.married
    address = pat.address
    address_pin = pat.address.pincode
    print(name, age, weight, height, bmi, address,address_pin, ':Data Inserted Successfully')
 
 
# Patient data are sended for validation to Patient model
patient_type = Patient(**data)

# insert function called
insert_patient_data(patient_type) 

# if doctor want to see his patients data on his appliciton, so we can send json data formate to client side !!
patient_json = patient_type.model_dump_json()
print("JSON FORMATE DATA:",patient_json)


# Better organization of related data (e.g., vitals, address, insurance)
# Reusability: Use Vitals in multiple models (e.g., Patient, MedicalRecord)
# Readability: Easier for developers and API consumers to understand
# Validation: Nested models are validated automatically—no extra work needed




# DATA FLOW
# [data collect from client side] -> [sent to Validators to Verify data/types] -> [varified data stored in Database]

# Role of API in DATA FLOW
# api's handle all client request and server response, make connection between client <-> server manage dataflow