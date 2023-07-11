from django.urls import path, include
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('main', views.analysisView)

urlpatterns = [
    path("home/", views.home, name="home"),
    path("", views.login_view),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("user_request/", views.user_request, name="user_request"),
    path("reject/<int:myid>/", views.reject, name="reject"),
    path("create/", views.admin_create, name="create"),
    path("view/", views.view, name="view"),
    path("update_view/<int:myid>/", views.update_view, name="update_view"),
    path("delete_view/<int:myid>/", views.delete_view, name="delete_view"),
    path("dictionary/", views.dictionary, name="dictionary"),
    path("add_word/", views.add_word, name="add_word"),
    path("delete_word/<int:myid>/", views.delete_word, name="delete_word"),

    path("analysis/", views.tweetsAnalysis),
    path("api/", include(router.urls)),
    path("table/", views.table, name="table"),
    path("tweetRetrieval/", views.tweetRetrieval, name="tweetRetrieval"),
    path("twitterUserRetrieval/", views.twitterUserRetrieval, name="twitterUserRetrieval"),

    path('customer_record/<int:myid>', views.select_cust, name='customer_record'),
    path('suspend_record/<int:myid>', views.suspend_view, name="suspend_record"),
    path('update_record/<int:myid>', views.update_view, name="update_record"),
    path('reinstate_record/<int:myid>', views.reinstate_view, name="reinstate_record")
]