from django.conf.urls import url, include
from django.conf import settings 
from django.views.static import serve
from django.contrib import admin

from Users.views import *

from Users.admin_views import *
from Users.admin_video_views import *

from Users.sign_up_views import *
from Users.video_views import *
from Users.generate_workout_views import *
from Users.user_stat_views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin-blog/', Admin_Blog, name='AdminBlog'),
    url(r'^admin-blog-posts/', Admin_Blog_Posts, name='AdminBlogPosts'),
    url(r'^admin-blog-post-detail/(?P<pk>\d+)/$', Admin_Blog_Posts_Detail, name='AdminBlogPostsDetail'),

    url(r'^admin-login/', Admin_Login, name='AdminLogin'),
    url(r'^admin-logout/', Admin_Logout, name='AdminLogout'),

    url(r'^admin-users/', Admin_Users, name='AdminUsers'),
    url(r'^admin-users-view-profile/', Admin_User_Profile, name='AdminUser_Profile'),

    url(r'^admin-workouts/', Admin_Workouts, name='Home'),

    url(r'^admin-exercises/', AdminExercises, name='Home'),

    url(r'^admin-videos/', Admin_Videos, name='Home'),
    url(r'^admin-videos-2/', Admin_Videos_2, name=''),    
    url(r'^admin-videos-library/', Admin_Videos_Library, name='Home'),
    url(r'^admin-videos-library-edit/', Admin_Videos_Edit, name='Home'),

    url(r'^blog/', Blog, name="Blog"), 

    url(r'^ckeditor/', include('ckeditor_uploader.urls')),


    url(r'^$', Home, name='Home'),
    url(r'^waiver/', Waiver, name='SignUpConfirmation'),
    url(r'^terms-conditions/', Terms_Conditions, name='SignUpConfirmation'),

    url(r'^sign-up-confirmation/', SignUp_Confirmation, name='SignUpConfirmation'),
    url(r'^renew-membership/', Membership_Expired, name='MembershipExpired'),

    url(r'^welcome/', Welcome, name='Welcome'),

    url(r'^welcome/', SignUp_Confirmation, name='SignUpConfirmation'),

    url(r'^tutorial/', Tutorial, name="tutorial"),
    url(r'^exercise-descriptions/', Exercise_Descriptions, name="exercise_descriptions"),

    url(r'^userpage/', User_Page, name="userpage"),
    # url(r'^userpage/', User_Page_Test, name="userpage"),

    url(r'^userpage-alloy/', User_Page_Alloy, name="userpage_alloy"),

    url(r'^contact/', Contact_And_Support, name="contact"),
    url(r'^progress-report/', Level_Up, name="levelup"),
    url(r'^get-workouts/', Get_Workout_Block, name='get_workout_block'),


    url(r'^userpageUpdate/', Workout_Update, name="userpageUpdate"),
    url(r'^userpageRPEUpdate/', RPE_Update, name="userpageRPEUpdate"),
    
    url(r'^profile-view/', User_Profile, name="userprofile"),
    url(r'^profile-stats/', User_Stats, name="user_stats"),

    url(r'^profile-view-workout/', User_Profile_View_Workout, name="profile_view_workout"),

    url(r'^videos/', Videos, name="videos"),

    url(r'^logout/', Logout, name='logout'),

    # url(r'^past-workouts/', Past_Workouts, name="pastworkouts"),
]

# serving media files only on debug mode
if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT
        }),
    ]
