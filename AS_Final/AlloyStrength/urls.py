from django.conf.urls import url, include
from django.contrib import admin
# from Users.views import Home, Member_Home, Admin, Test, User_Page, Workout_Update, Videos, AdminExercises, RPE_Update, SignUp_Confirmation, Welcome, Past_Workouts, User_Profile, Level_Up
from django.conf import settings
from django.conf.urls.static import static
from Users.views import *

from Users.admin_views import *
from Users.admin_video_views import *


from Users.sign_up_views import *
from Users.video_views import *
from Users.generate_workout_views import *
from Users.user_stat_views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^admin-login/', Admin_Login, name='AdminLogin'),
    url(r'^admin-logout/', Admin_Logout, name='AdminLogout'),

    url(r'^admin-users/', Admin_Users, name='AdminUsers'),
    url(r'^admin-users-view-profile/', Admin_User_Profile, name='AdminUser_Profile'),
    url(r'^admin-users-view-profile-workout/', Admin_User_Workout, name='AdminUser_Workout'),

    url(r'^admin-workouts/', Admin_Workouts, name='Home'),

    url(r'^admin-exercises/', AdminExercises, name='Home'),

    url(r'^admin-videos/', Admin_Videos, name='Home'),
    url(r'^admin-videos-2/', Admin_Videos_2, name=''),    
    url(r'^admin-videos-library/', Admin_Videos_Library, name='Home'),
    url(r'^admin-videos-library-edit/', Admin_Videos_Edit, name='Home'),


    url(r'^$', Home, name='Home'),
    url(r'^coach-biographies', coach_biographies, name='coach_biogrpahies'), 
    url(r'^contact', contact, name='contact'),
    url(r'^why-alloy-strength', why_alloy_strength, name='why_alloy_strength'),
    url(r'^terms-and-conditions', terms_and_conditions, name='terms_and_conditions'),
    url(r'^home', home, name='home'),
    
    

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

    url(r'^contact_and_support/', Contact_And_Support, name="contact_and_support"),
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

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
