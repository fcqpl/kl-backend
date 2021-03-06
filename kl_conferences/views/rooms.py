from django.http import HttpResponseRedirect
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from kl_conferences.bbb_api import BigBlueButtonAPI
from kl_conferences.models.room import Room
from kl_conferences.serializers.room_serializer import RoomSerializer
from kl_participants.models import Student


def limbo_url(token):
    return f'{settings.DOMAIN}/#/limbo/?token={token}'


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all().order_by('-id')
    serializer_class = RoomSerializer

    @action(detail=False, methods=['get'], url_path='join/(?P<token>[^/]+)/?', permission_classes=[])
    def join(self, request, token):
        token = token.upper()
        student = get_object_or_404(Student, access_token=token)
        lesson = Room.objects.filter(group=student.group).last()
        if not lesson:
            return HttpResponseRedirect(redirect_to=limbo_url(token))

        bbb_api = BigBlueButtonAPI(lesson.server_node.hostname, lesson.server_node.api_secret)
        if not bbb_api.is_meeting_running(lesson.bbb_meeting_id):
            # TODO - soft delete?
            lesson.delete()
            return HttpResponseRedirect(redirect_to=limbo_url(token))

        try:
            # TODO - where do I take pass from?
            redirect_url = bbb_api.get_join_url(
                meeting_id=lesson.bbb_meeting_id,
                password=lesson.attendee_secret,
                join_as=student.display_name,
                assing_user_id=student.uuid,
            )
        except:
            # TODO - too broad
            return HttpResponseRedirect(redirect_to=limbo_url(token))

        return HttpResponseRedirect(redirect_to=redirect_url)
