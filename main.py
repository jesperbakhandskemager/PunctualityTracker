import bs4 as bs
import requests
import json
import urllib3
from datetime import datetime, timedelta, time
urllib3.disable_warnings()

class Student:
    def __init__(self, name, total_times, total_minutes, total_days, average_time):
        self.name = name
        self.total_times = total_times
        self.total_minutes = total_minutes
        self.total_days = total_days
        self.average_time = average_time

class StudentEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return {
                "name": obj.name,
                "total_times": obj.total_times,
                "total_minutes": obj.total_minutes,
                "total_days": obj.total_days,
                "average_time": str(obj.average_time)
            }
        return super().default(obj)


def get_all_student_data():
    student_ids = get_all_student_ids()
    students = []
    for student_id in student_ids:
        student = get_student_data(student_id)
        if student.name == "Null":
            continue
        students.append(student)
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

    if len(times) == 0:
        return Student("Null", 0, 0, 0, 0)
    
    # Convert time objects to time durations in seconds
    durations = [t.hour * 3600 + t.minute * 60 + t.second for t in times]

    # Calculate the average time duration
    average_duration = sum(durations) / len(durations)

    # Convert the average time duration back to the time format
    average_time = time(
        int(average_duration // 3600),
        int((average_duration % 3600) // 60),
        int(average_duration % 60)
    )
            
    return Student(student_name, total_times, minutes_total, total_days, average_time)



students = get_all_student_data()
file_content = json.dumps(students, cls=StudentEncoder)

f = open("data.json", "w")
f.write(file_content)
f.close()

# # Sort the array based on total_minutes in descending order
# sorted_array = sorted(students, key=lambda x: x.total_times / x.total_days if x.total_days != 0 else 0, reverse=True)
# # sorted_array = sorted(students, key=lambda x: x.total_minutes, reverse=True)

# i = 0
# # Print the sorted array
# for item in sorted_array:
#     if item.total_times == 0:
#         continue
#     i += 1
#     hours = round(item.total_minutes / 50, 2)
#     percent_late = round((item.total_times / item.total_days) * 100, 2)
#     print(f"{str(i)}) Name: {item.name}, Total Times: {item.total_times} / {item.total_days} = {percent_late}%, Total Minutes: {item.total_minutes}, Total Hours: {hours}, Average time: {item.average_time}")