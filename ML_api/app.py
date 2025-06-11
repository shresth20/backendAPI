from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field  
from typing import Annotated, Literal, Optional
import pickle
import pandas as pd


# LOAD ML MODEL
with open('model.pkl','rb') as f:
    model = pickle.load(f)



app = FastAPI()


tier1=["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]    
tier2=[
"Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
"Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
"Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
"Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
"Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
"Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]
# DATA VALIDATION
class userInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description='Enter user Age in Years')]
    weight: Annotated[float, Field(..., gt=0, description='Enter Weight in Kgs')]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description='Enter Height in Meters')]
    income_lpa: Annotated[float, Field(..., gt=0, description='Enter Income in LPA')]
    smoker: Annotated[bool, Field(..., description='Choose user Smoker or not')]
    city: Annotated[str, Field(..., max_length=15, description='Enter user City')]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job','business_owner', 'unemployed', 'private_job'], Field(..., description=f'Enter user Occupation:')]

    @computed_field
    @property
    def bmi(self)->float:
        bmi= round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def age_group(self)->str:
        if 0 < self.age < 18:
            return "child"
        elif 18 <= self.age < 30:
            return "young"
        elif 30 <= self.age <= 45:
            return "middle_aged"
        else:
            return "senior"
        
    @computed_field
    @property
    def lifestyle_risk(self)-> str:
        if self.smoker and self.bmi>30:
            return "high"
        elif self.smoker or self.bmi>27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def city_tier(self)->int:
        if self.city in tier1:
            return 1
        elif self.city in tier2:
            return 2
        else:
            return 3

# API's
@app.post('/predict')
def predict_premium(data:userInput):

    input_df = pd.DataFrame([{
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lifestyle_risk,
        'city_tier':data.city_tier,
        'income_lpa':data.income_lpa,
        'occupation': data.occupation,
          }])
    
    # calling ML model predict method
    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={'predicted_category':prediction})













