import os
import django
from django.utils import timezone
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Attendance.settings')
django.setup()

from telles.models import CustomUser, StudentProfile, Attendance, AttendanceLog

def run_test():
    print("Starting AttendanceLog verification...")

    # Teardown previous test data
    CustomUser.objects.filter(username='test_student_log').delete()
    
    # 1. Create User & Student
    user = CustomUser.objects.create_user(username='test_student_log', password='password')
    student = StudentProfile.objects.create(user=user, student_name='Test Student Log', student_number=9999)
    print(f"Created student: {student}")

    # 2. Simulate First Submission (Late)
    today = date.today()
    time1 = timezone.now()
    
    # Logic from views.py
    Att_obj, _ = Attendance.objects.update_or_create(
        student=student,
        date=today,
        defaults={
            "status": "late",
            "reason": "Train delay",
            "checked": False,
            "time": time1
        }
    )
    AttendanceLog.objects.create(
        student=student,
        date=today,
        time=time1,
        status="late",
        reason="Train delay"
    )
    print("Submitted 'Late'")

    # 3. Simulate Second Submission (Absent)
    time2 = timezone.now()
    Att_obj_2, _ = Attendance.objects.update_or_create(
        student=student,
        date=today,
        defaults={
            "status": "absent",
            "reason": "Feeling sick",
            "checked": False,
            "time": time2
        }
    )
    AttendanceLog.objects.create(
        student=student,
        date=today,
        time=time2,
        status="absent",
        reason="Feeling sick"
    )
    print("Submitted 'Absent'")

    # 4. Verification
    
    # Check Attendance (should be Absent)
    current_attendance = Attendance.objects.get(student=student, date=today)
    if current_attendance.status != 'absent':
        print(f"FAIL: Current status is {current_attendance.status}, expected 'absent'")
    else:
        print("PASS: Current status is 'absent'")

    # Check Logs (should have 2)
    logs = AttendanceLog.objects.filter(student=student, date=today).order_by('time')
    if logs.count() != 2:
        print(f"FAIL: Log count is {logs.count()}, expected 2")
    else:
        print("PASS: Log count is 2")
        print(f"  Log 1: {logs[0].status} at {logs[0].time}")
        print(f"  Log 2: {logs[1].status} at {logs[1].time}")

    # Cleanup
    # user.delete() # Keep for manual check if needed, or delete
    print("Test finished.")

if __name__ == '__main__':
    run_test()
