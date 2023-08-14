from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('main', views.analysisView)

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("", views.login_view),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    path("home/", views.home, name="home"),
    path("customer_request/", views.customer_request, name="customer_request"),
    path("approve/<int:myid>/", views.approve, name="approve"),
    path("reject/<int:myid>/", views.reject, name="reject"),
    path("create/", views.admin_create, name="create"),
    path("view/", views.view, name="view"),
    path("update_view/<int:myid>/", views.update_view, name="update_view"),
    path("delete_view/<int:myid>/", views.delete_view, name="delete_view"),
    path("dictionary/", views.dictionary, name="dictionary"),
    path("add_word/", views.add_word, name="add_word"),
    path("delete_word/<int:myid>/", views.delete_word, name="delete_word"),

    path("customer/", views.customer, name="customer"),
    path("view_profile/", views.view_profile, name="view_profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("delete_profile/", views.delete_profile, name="delete_profile"),

    path("analysis/", views.tweetsAnalysis),
    path("api/", include(router.urls)),
    path("chart/", views.adminChart, name="chart"),
    path("cchart/", views.custChart, name="cchart"),
    path("retrieve/", views.webScrapper, name="retrieve"),
    path("cretrieve/", views.cwebScrapper, name="cretrieve"),
    path("search/", views.tweetSearch, name="search"),
    path("csearch/", views.ctweetSearch, name="csearch"),
    path('twitterUser/<str:myid>', views.twitterUserRetrieval, name='twitter_user'),
    path('ctwitterUser/<str:myid>', views.ctwitterUserRetrieval, name='ctwitter_user'),

    path('customer_record/<int:myid>', views.select_cust, name='customer_record'),
    path('suspend_record/<int:myid>', views.suspend_view, name="suspend_record"),
    path('update_record/<int:myid>', views.update_view, name="update_record"),
    path('reinstate_record/<int:myid>', views.reinstate_view, name="reinstate_record"),

    path("send_email/", views.send_email, name="send_email")
]