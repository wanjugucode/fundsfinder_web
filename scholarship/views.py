from django.shortcuts import render
from .scrape_scholarships import Command

def scholarship_list(request):
    # This code snippet creates an instance of a Command class and then calls its handle method to retrieve scholarships
    command = Command()
    scholarships = command.handle()
    return render(request, 'index.html', {'scholarships': scholarships})

   
