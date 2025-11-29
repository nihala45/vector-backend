from django.urls import path
from .views import ProducCRUDView, CreateCourseView, AddStaffToCourse, ClearCourseStaff, RemoveStaffFromCourse, ModuleCreateAndListView, ModuleCRUDView, TopicCreateAndListView, TopicCRUDView, VideoCreateAndListView,VideoCRUDView, DocumentCRUDView, DocumentCreateAndListView

urlpatterns = [
    path("", CreateCourseView.as_view(), name="course-create"),
    path("<int:pk>/", ProducCRUDView.as_view(), name="course-crud"),
    path("<int:course_id>/add-staff/", AddStaffToCourse.as_view(), name="add-staff-to-course"),
    path("<int:course_id>/clear-staff/", ClearCourseStaff.as_view(), name="clear-course-staff"),
    path("<int:course_id>/remove-staff/", RemoveStaffFromCourse.as_view(), name="remove-staff-from-course"),
    path("/modules/", ModuleCreateAndListView.as_view(), name="module-create-list"),
    path("/modules/<int:pk>/", ModuleCRUDView.as_view(), name="module-crud"),
    path("/topics/", TopicCreateAndListView.as_view(), name="topic-create-list"),   
    path("/topics/<int:pk>/", TopicCRUDView.as_view(), name="topic-crud"),
    path("/videos/", VideoCreateAndListView.as_view(), name="video-create-list"),
    path("/videos/<int:pk>/", VideoCRUDView.as_view(), name="video-crud"),
    path("/documents/", DocumentCreateAndListView.as_view(), name="document-create-list"),  
    path("/documents/<int:pk>/", DocumentCRUDView.as_view(), name="document-crud"),
]