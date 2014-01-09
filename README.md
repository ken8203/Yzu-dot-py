from yzu import *
student = Yzu(username, password)

1)student.get_course_credits()

Response format:
{semester: [[course_code, course_name, course_credit, course_grade], [...], [...], .....], semester_2: [[course_code, course_name, course_credit, course_grade], [...], [...], .....], ...}

2)student.get_classic_point()

Response format:
{semester: [[time, teacher, book_name, category, point, note], [...], [...], .....], semester_2: [[time, teacher, book_name, category, point, note], [...], [...], .....], ...}

3)student.get_serving_point()

Response format:
[point_of_serving, point_of_activity]

4)student.get_all_course(semester_you_want)

You can edit the code at 224 lines to do I/O or anything you want.