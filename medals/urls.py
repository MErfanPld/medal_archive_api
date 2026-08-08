from rest_framework.routers import DefaultRouter

from .views import MedalViewSet

app_name = 'medals'

router = DefaultRouter()
router.register('', MedalViewSet, basename='medal')

urlpatterns = router.urls
