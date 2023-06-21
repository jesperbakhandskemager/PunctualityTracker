import bs4 as bs
import requests
import urllib3
from datetime import datetime
urllib3.disable_warnings()

class Student:
    def __init__(self, name, total_times, total_minutes, total_days):
        self.name = name
        self.total_times = total_times
        self.total_minutes = total_minutes
        self.total_days = total_days


def get_all_student_data():
    student_ids = get_all_student_ids()
    students = []
    for student_id in student_ids:
        students.append(get_student_data(student_id))
    return students


def get_all_student_ids():
    source = requests.get('http://instrukdb/elev_oversigt.html', verify=False)
    soup = bs.BeautifulSoup(source.text,'lxml')
    studentIds = []
    all_tr = soup.find_all('tr')
    for tr in all_tr:
        content = tr.contents[0]
        for url in content.find_all('a'):
            studentIds.append(url.get('href'))
    return studentIds

def get_student_data(student_string):
    form_data = {'showAll': 'Udvid+Logs'}
    source = requests.post(f'https://instrukdb/{student_string}', data=form_data, verify=False)
    soup = bs.BeautifulSoup(source.text,'lxml')

    times = []
    reference_time_str = "09:00"
    reference_time_obj = datetime.strptime(reference_time_str, "%H:%M").time()

    all_tr = soup.find_all('tr')
    student_name = all_tr[1].text
    
    minutes_total = 0
    total_times = 0
    total_days = 0

    for tr in all_tr:
        i = 0
        for td in tr:
                if i == 2:
                    if len(td.text) == 13:
                        if not td.text[0].isdigit() or not td.text[1].isdigit():
                            continue
                        total_days += 1
                        clean = td.text.split()
                        time_obj = datetime.strptime(clean[0], "%H:%M").time()
                        times.append(time_obj)
                    i = 0
                i += 1



    for day in times:
        time_difference = datetime.combine(datetime.today(), day) - datetime.combine(datetime.today(), reference_time_obj)
        minutes_difference = int(time_difference.total_seconds() / 60)
        too_late = minutes_difference >= 1
        
        if too_late:
            total_times += 1
            minutes_total += minutes_difference
            
    return Student(student_name, total_times, minutes_total, total_days)



students = get_all_student_data()

# Sort the array based on total_minutes in descending order
sorted_array = sorted(students, key=lambda x: x.total_times / x.total_days if x.total_days != 0 else 0, reverse=True)
# sorted_array = sorted(students, key=lambda x: x.total_minutes, reverse=True)

i = 0
# Print the sorted array
for item in sorted_array:
    if item.total_times == 0:
        continue
    i += 1
    hours = round(item.total_minutes / 50, 2)
    percent_late = round((item.total_times / item.total_days) * 100, 2)
    print(f"{str(i)}) Name: {item.name}, Total Times: {item.total_times} / {item.total_days} = {percent_late}%, Total Minutes: {item.total_minutes}, Total Hours: {hours}")