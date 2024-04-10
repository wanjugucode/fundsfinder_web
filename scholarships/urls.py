from django.urls import path
from . import views


urlpatterns=[
    path('scholarships',views.scholarships_list, name="scholarships"),
    path('',views.landing_page, name="landing_page"),
    path('admin_scholarships_view',views.admin_scholarships_view, name="admin_scholarships_view"),
    path('addscholarship',views.add_scholarship,name='addscholarship'),
    path('editscholarship/<int:id>/',views.edit_scholarship, name='editscholarship'),
    path('removescholarship/<int:id>/',views.remove_scholarship, name='removescholarship'),
    path('dashboard',views.dashboard, name='dashboard'),
    path('users_profile',views.users_profile, name='users_profile'),
    path('add_admin/', views.add_admin, name='add_admin'),
    path('revoke/', views.add_admin, name='revoke'),
    path('users/', views.users_list, name='users'),

    path('apply_scholarship/<int:scholarship_id>/',views.apply_scholarship, name="applyscholarship"),
    path('applicants_list/',views.applicants_list, name='applicants_list'),
    path('approve_scholarship/<int:id>/',views.approve_scholarship, name='approve_scholarship'),
    path('approved_list/',views.approved_list, name='approved_list'),
    path('bookmarks/',views.bookmarks, name='bookmarks'),
    path('bookmark/<int:scholarship_id>/', views.bookmark_scholarship, name='bookmark_scholarship'),
    path('remove_bookmark/<int:scholarship_id>/', views.remove_bookmark, name='remove_bookmark'),
    path('applicant_history/',views.application_history, name='applicant_history'),
    path('approved_application/',views.approved_scholarships, name='approved_application'),
    path('add_comment/<int:scholarship_id>/', views.add_comment, name='add_comment'),
    path('add_rating/<int:scholarship_id>/', views.add_rating, name='add_rating'),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('edit_rating/<int:rating_id>/', views.edit_rating, name='edit_rating'),
    path('delete_rating/<int:rating_id>/', views.delete_rating, name='delete_rating'),
    path('add_report/<int:scholarship_id>/', views.report_inaccuracy, name='add_report'),
    path('view_report/<int:scholarship_id>/', views.view_report, name='view_report'),
    path('index',views.index,name='home'),
    path('support',views.support_page, name="support"),



    path('item/',views.item, name='item'),
    ]