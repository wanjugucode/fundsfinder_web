from django.urls import path
from . import views


urlpatterns=[
    path('scholarships',views.scholarships_list, name="scholarships"),
    path('admin_scholarships_view',views.admin_scholarships_view, name="admin_scholarships_view"),
    path('addscholarship',views.add_scholarship,name='addscholarship'),
    path('editscholarship/<int:id>/',views.edit_scholarship, name='editscholarship'),
    path('removescholarship/<int:id>/',views.remove_scholarship, name='removescholarship'),
    path('apply_scholarship',views.apply_scholarship, name="applyscholarship"),
    path('applicants_list/',views.applicants_list, name='applicants_list'),
    path('approve_scholarship/<int:id>/',views.approve_scholarship, name='approve_scholarship'),
    path('approved_list/',views.approved_list, name='approved_list'),
    path('bookmarks/',views.bookmarks, name='bookmarks'),
    path('bookmark/<int:scholarship_id>/', views.bookmark_scholarship, name='bookmark_scholarship'),
    path('applicant_history/',views.application_history, name='applicant_history'),
    path('approved_application/',views.approved_scholarships, name='approved_application'),



    ]