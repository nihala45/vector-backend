from django.shortcuts import render
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from .serializer import CourseSerializer
from .models import Course
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

# Create your views here.
class CreateCourseView(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
class ProducCRUDView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
class AddStaffToCourse(APIView):
    def post(self, request, course_id):
        staff_ids = request.data.get('staff_ids', [])
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        staff_members = course.staff.model.objects.filter(id__in=staff_ids, role='staff')
        if not staff_members:
            return Response({'error': 'No valid staff members found'}, status=400)
        course.staff.add(*staff_members)
        return Response({
            'msg': 'Staff members added successfully',
            'course_id': course.id,
            'staff_added': [staff.id for staff in staff_members]
            }, status=200)
        
class ClearCourseStaff(APIView):
    def delete(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        
        course.staff.clear()
        return Response({
            'msg': 'All staff members removed from the course successfully',
            'course_id': course.id
            }, status=200)
        
class RemoveStaffFromCourse(APIView):
    def delete(self, request, course_id):
        staff_ids = request.data.get('staff_ids', [])
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        
        staff_members = course.staff.model.objects.filter(id__in=staff_ids, role='staff')
        if not staff_members:
            return Response({'error': 'No valid staff members found'}, status=400)
        
        course.staff.remove(*staff_members)
        return Response({
            'msg': 'Staff members removed successfully',
            'course_id': course.id,
            'staff_removed': [staff.id for staff in staff_members]
            }, status=200)

