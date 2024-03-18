# management/commands/scrape_scholarships.py
from django.core.management.base import BaseCommand
from .models import Scholarship
import requests
from bs4 import BeautifulSoup

class Command(BaseCommand):
    def handle(self, *args, **options):
        url = 'https://bold.org/scholarships/by-year/graduate-students-scholarships/'
        response = requests.get(url)
        scholarships = []

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print('soup')

            for scholarship in soup.find_all('li', class_='ScholarshipGroupContainer-module--scholarshipContainer--28fef'):
                name = scholarship.find('h3', class_="SimpleScholarshipItem-module--name--a8f17").text.strip()
                amount = scholarship.find('span', class_='SimpleScholarshipItem-module--amount--47b1e').text.strip()
                deadline = scholarship.find('div', class_="SimpleScholarshipItem-module--deadline--bb492")
                if deadline != None:
                    deadline = deadline.find_all('span')[2].text.strip()
                egligibility_criteria = scholarship.find('div', class_="SimpleScholarshipItem-module--eligibilityDetails--2ff00")
                if egligibility_criteria != None:
                    egligibility_criteria = egligibility_criteria.text.strip()
                apply_link = scholarship.find('a', class_="SimpleScholarshipItem-module--container--eeab6")
                if apply_link:
                    apply = apply_link['href']
                else:
                    apply = None



                # apply=scholarship.find('div', class_="ScholarshipItem-module--title--3uU1d").find('a')['href']

                # apply=scholarship.find('button', class_="Button-module--button--54905 Button-module--small--715d5 Button-module--primary--9ed87 Button-module--fluid--e4e8b").text.strip()

                scholarships.append((name,amount, deadline,egligibility_criteria,apply))
            Scholarship.objects.all().delete()  
            for scholarship in scholarships:
                print(f"Adding scholarship: {scholarship} ")
                instance = Scholarship(name=scholarship)
                instance.save()
            self.stdout.write(self.style.SUCCESS('Successfully scraped scholarships'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch scholarships'))

        return scholarships
