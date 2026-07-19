from types import SimpleNamespace

from django.shortcuts import render

from predictor.excel_loader import load_student_records
from predictor.models import Student


try:
    Student.objects.exists()
except Exception:
    Student = None


class StudentRecord(SimpleNamespace):
    def get_status_display(self):
        status_labels = {
            "placed": "Placed",
            "in-progress": "In Progress",
            "not-placed": "Not Placed",
        }
        return status_labels.get(self.status, self.status.replace("-", " ").title())


def _load_excel_students():
    try:
        records = load_student_records()
    except Exception:
        return []

    return [
        StudentRecord(
            name=record.get("name", ""),
            year=record.get("year", ""),
            company_name=record.get("company_name", ""),
            branch=record.get("branch", ""),
            package_lpa=record.get("package", "-"),
            status=record.get("status", "placed"),
        )
        for record in records
    ]


def home(request):
    return render(request, 'predictor/index.html')


def predict(request):
    if request.method == "POST":
        algorithm = request.POST.get("algorithm")
        if algorithm == "decision_tree":
            return result_dt(request)
        if algorithm == "random_forest":
            return result_rfc(request)
        return render(
            request,
            "predictor/predict.html",
            {
                "error": "Please select a prediction algorithm.",
                "selected_algorithm": algorithm,
            },
        )

    return render(request, 'predictor/predict.html')


def students(request):
    students = []
    if Student is not None:
        try:
            students = list(Student.objects.all())
        except Exception:
            students = []

    if not students:
        students = _load_excel_students()

    return render(request, 'predictor/students.html', {"students": students})


def companies(request):
    return render(request, 'predictor/companies.html')

def algorithms(request):
    return render(request, 'predictor/algorithms.html')



# """
import os
import joblib
from django.conf import settings
import pandas as pd

model_path_dt = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'placement_predict_dt_model.pkl')
encoder_path_dt = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'label_encoders_dt.pkl')

model_path_rfc = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'placement_predict_rfc_model.pkl')
encoder_path_rfc = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'label_encoders_rfc.pkl')



model_dt = joblib.load(model_path_dt)
label_encoders_dt = joblib.load(encoder_path_dt)

model_rfc = joblib.load(model_path_rfc)
label_encoders_rfc = joblib.load(encoder_path_rfc)



def result_dt(request):
    if request.method == "POST":
        data = request.POST
        features = [
            int(data['IQ Score']),
            float(data['Previous Semester Result']),
            float(data['CGPA']),
            int(data['Academic Performance']),
            label_encoders_dt['Internship_Experience'].transform([data['Internship Experience']])[0],
            int(data['Extra-Curricular Score']),
            int(data['Communication Skills']),
            int(data['Projects Completed']),
        ]

        # Feature names must match training
        feature_names = [
            "IQ", "Prev_Sem_Result", "CGPA", "Academic_Performance", "Internship_Experience",
            "Extra_Curricular_Score", "Communication_Skills", "Projects_Completed"
        ]

        df_input = pd.DataFrame([features], columns= feature_names)
        yes_no = model_dt.predict(df_input)[0]
        # Choose emoji based on score
        if yes_no:
            emoji = "😊"
            msg = "Congratulations! as per our prediction you will be placed."
        else:
            emoji = "😟"
            msg = "Sorry as per our prediction you won't be placed."

        name = data['Name']

        context = {
            "yes_no": yes_no,
            "emoji": emoji,
            "msg": msg,
            "name": name,
            "selected_algorithm": "decision_tree",
            "algorithm_name": "Decision Tree Algorithm",
        }
        return render(request, "predictor/predict.html", context)

    return render(request, "predictor/predict.html")

# """


def result_rfc(request):
    if request.method == "POST":
        data = request.POST
        features = [
            int(data['IQ Score']),
            float(data['Previous Semester Result']),
            float(data['CGPA']),
            int(data['Academic Performance']),
            label_encoders_rfc['Internship_Experience'].transform([data['Internship Experience']])[0],
            int(data['Extra-Curricular Score']),
            int(data['Communication Skills']),
            int(data['Projects Completed']),
        ]

        # Feature names must match training
        feature_names = [
           "IQ", "Prev_Sem_Result",	"CGPA",	"Academic_Performance",	"Internship_Experience",
            "Extra_Curricular_Score", "Communication_Skills", "Projects_Completed"
        ]

        df_input = pd.DataFrame([features], columns= feature_names)
        yes_no = model_rfc.predict(df_input)[0]
        # Choose emoji based on score
        if yes_no:
            emoji = "😊"
            msg = "Congratulations! as per our prediction you will be placed."
        else:
            emoji = "😟"
            msg = "Sorry as per our prediction you won't be placed."

        name = data['Name']

        context = {
            "yes_no": yes_no,
            "emoji": emoji,
            "msg": msg,
            "name": name,
            "selected_algorithm": "random_forest",
            "algorithm_name": "Random Forest Classifier Algorithm",
        }
        return render(request, "predictor/predict.html", context)

    return render(request, "predictor/predict.html")

