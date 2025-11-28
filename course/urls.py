from django.urls import path
from .views import ProducCRUDView, CreateCourseView, AddStaffToCourse, ClearCourseStaff, RemoveStaffFromCourse

urlpatterns = [
    path("", CreateCourseView.as_view(), name="course-create"),
    path("<int:pk>/", ProducCRUDView.as_view(), name="course-crud"),
    path("<int:course_id>/add-staff/", AddStaffToCourse.as_view(), name="add-staff-to-course"),
    path("<int:course_id>/clear-staff/", ClearCourseStaff.as_view(), name="clear-course-staff"),
    path("<int:course_id>/remove-staff/", RemoveStaffFromCourse.as_view(), name="remove-staff-from-course"),
]