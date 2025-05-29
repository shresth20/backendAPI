from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field  
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

# DATA VALIDATION

# validate new patient data
class Patient(BaseModel):
    Id: Annotated[str, Field(..., max_length=5, example='P001')]
    name: Annotated[str, Field(...,max_length=50, title='Enter patient name')]
    city: Annotated[str, Field(..., max_length=50, title='Enter patient city')]
    gender: Annotated[str, Literal['male', 'female', 'other'], Field(..., title='Enter patient gender', description="Entre patient gender:'male' or 'female' or 'other' ")]
    age: Annotated[int, Field(..., gt=0, lt=120, title='', description='Enter patient age in Years')]
    height: Annotated[float, Field(..., gt=0, lt=5, title='', description='Enter patient height in Meters')]
    weight: Annotated[float, Field(..., gt=0, title='', description='Enter patient weight in Kg')]

    @computed_field
    @property
    def bmi(self)-> float:
        bmi= round(self.weight/(self.height**2),2)
        return bmi

    @computed_field
    @property
    def verdict(self)-> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Overweight'
        elif self.bmi < 35:
            return 'Obese'
        else:
            return 'Extremely Obese'

# validate update pateint data
class Patient_Update(BaseModel):
    name: Annotated[Optional[str], Field(default=None, max_length=50, title='Enter patient name')]
    city: Annotated[Optional[str], Field(default=None, max_length=50, title='Enter patient city')]
    gender: Annotated[Optional[Literal['male', 'female', 'other']], Field(default=None, title='', description="Entre patient gender:'male' or 'female' or 'other' ")]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120, title='',)]
    height: Annotated[Optional[float], Field(default=None, gt=0, lt=5, title='',description='Enter patient height in Meters')]
    weight: Annotated[Optional[float], Field(default=None, gt=0, title='',description='Enter patient weight in Kg')]


# load data form database
def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

# save data form database
def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f, indent=2)



# API's

# home page
@app.get("/")
def home():
    return {"msg": "Patient Management System !!"}

# about page
@app.get("/about/{name}")
def about(name):
    return {"msg": f"This is my about page of fastapi project !!  welcome {name}"}

# view all patient data
@app.get('/view')
def view():
    data = load_data()
    return data

# select patient:id
@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description='access perticular patient data by ID', example='P001')):
    data = load_data()
    if patient_id in data:
        return data[f"{patient_id}"]
    else:
        raise HTTPException(status_code=404, detail='Patient Not Found')

# sort data 
@app.get('/sort')
def sort_patient(sort_by: str = Query(..., discription='sort patients by height, weight, age, bmi'), order: str = Query('asc', discription='order by "asc" and "des"')):
    data = load_data()

    # handle err
    sort_value = ["age", "height", "weight", "bmi"]
    if sort_by not in sort_value:
        raise HTTPException(status_code=400, detail=f'Invalid parameter select value from {sort_value}')
    if order not in ['asc', 'des']:
        raise HTTPException(status_code=400,detail='Invalid order, select "asc" or "des" ')

    sort_order = True if order == 'des' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(
        sort_by, 0), reverse=sort_order)
    return sorted_data

# create patient data
@app.post('/create')
def create_patient(new_patient :Patient):
    data = load_data()
    if new_patient.Id in data:
        raise HTTPException(status_code=400,  detail=f"Patient with Id {new_patient.Id} already exists")
    
    data[new_patient.Id] = new_patient.model_dump(exclude='id')
    save_data(data)
    return JSONResponse(status_code=201, content={'msg':'Patient CREATE Successfully'})
    
# update patient:id data
@app.put('/update/{patient_id}')
def Update_patient(patient_id:str, patient_update:Patient_Update):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,  detail=f"Patient with Id:{patient_id} does not exists")
    
    existing_patient_info = data[patient_id]
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value

    existing_patient_info["Id"] = patient_id

    verify_updated_patient = Patient(**existing_patient_info)
    verify_updated_patient = verify_updated_patient.model_dump(exclude="Id")

    data[patient_id] = verify_updated_patient
    save_data(data)
    return JSONResponse(status_code=201, content={'msg':'Patient Data UPDATE Successfully'})
    
# delete/patient:id data
@app.delete('/delete/{patient_id}')
def delete_patient_data(patient_id:str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,  detail=f"Patient with Id:{patient_id} does not exists")
    
    del data[patient_id]
    # data.pop(patient_id)
    save_data(data)
    return JSONResponse(status_code=201, content={'msg':'Patient Data DELETE Successfully'})




# test
if __name__ == '__main__':
    d = load_data()
    print(d.pop("P006"), d)
