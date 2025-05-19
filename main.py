from fastapi import FastAPI, Path, HTTPException, Query
import json
app = FastAPI()


def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data


@app.get("/")
def hello():
    return {"msg": "Patient Management System !!"}


@app.get("/about/{name}")
def about(name):
    return {"msg": f"this is my about page of fastapi project !!  welcome {name}"}


# create

# view all
@app.get('/view')
def view():
    data = load_data()
    return data

# patient:id


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
        raise HTTPException(
            status_code=400, detail=f'Invalid parameter select value from {sort_value}')
    if order not in ['asc', 'des']:
        raise HTTPException(status_code=400,
                            detail='Invalid order, select "asc" or "des" ')

    sort_order = True if order == 'des' else False
    sorted_data = sorted(data.values(), key=lambda x: x.get(
        sort_by, 0), reverse=sort_order)
    return sorted_data

# update/patient:id

# delete/patient:id


# test
if __name__ == '__main__':
    d = load_data()
    print(d.values())
