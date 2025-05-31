from tkinter import Widget
from django import forms
from .models import workAssignments,SalaryDisbursement
from .models import BusinessExpenditure, RequestType
# class workform(forms.ModelForm):
#     class Meta:
#         model=workAssignments
#         widgets={
#             "assignDate" : forms.DateInput(attrs={'type':'datetime-local'}),
#             "dueDate" : forms.DateInput(attrs={'type':'datetime-local'}),
#             }
#         labels={"assignerId" : "Select Your Id"}
        
#         fields=[
#             "assignerId",
#             "work",
#             "assignDate",
#             "dueDate",
#             "taskerId",

#         ]
        
##########################3

class SalaryDisbursementForm(forms.ModelForm):
    class Meta:
        model = SalaryDisbursement
        fields = ['employee', 'month', 'year', 'total_salary', 'status', 'salary_release_date']
        widgets = {
            'salary_release_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        salary_release_date = cleaned_data.get('salary_release_date')

        if status == 'Paid' and not salary_release_date:
            raise forms.ValidationError("Please provide a release date for the paid status.")

        return cleaned_data
    
################################################################################################class BusinessExpenditureForm:


from django import forms
from .models import ExpenditureRequest, LeaveRequest, OtherRequest
from datetime import datetime, timedelta

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = ExpenditureRequest
        fields = ['expenditure_name', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'expenditure_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }

class LeaveForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['title', 'from_date', 'to_date', 'message']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'from_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'to_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if from_date and to_date:
            if from_date > to_date:
                raise forms.ValidationError("End date must be after start date")
            
            # Calculate number of days excluding Sundays
            current_date = from_date
            days = 0
            while current_date <= to_date:
                if current_date.weekday() != 6:  # 6 is Sunday
                    days += 1
                current_date += timedelta(days=1)
            
            # Store the calculated days
            cleaned_data['days'] = days

        return cleaned_data

class OtherRequestForm(forms.ModelForm):
    class Meta:
        model = OtherRequest
        fields = ['title', 'message', 'date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

###################################################################
from django import forms
from .models import Task, Employee
from django.contrib.auth.models import User

class EmployeeAdminForm(forms.ModelForm):
    create_user_account = forms.BooleanField(
        required=False,
        label='Create user account automatically',
        help_text='Check this to automatically create a user account for this employee'
    )
    
    class Meta:
        model = Employee
        fields = '__all__'

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['employee', 'task_details', 'assign_date', 'due_date']

    employee = forms.ModelChoiceField(queryset=Employee.objects.all(), empty_label="Select Employee")
    assign_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    due_date = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
