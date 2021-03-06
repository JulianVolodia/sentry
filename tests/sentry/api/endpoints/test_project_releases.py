from __future__ import absolute_import

from datetime import datetime
from django.core.urlresolvers import reverse

from sentry.models import Release
from sentry.testutils import APITestCase


class ProjectReleaseListTest(APITestCase):
    def test_simple(self):
        self.login_as(user=self.user)

        team = self.create_team(owner=self.user)
        project1 = self.create_project(team=team, name='foo')
        project2 = self.create_project(team=team, name='bar')

        release1 = Release.objects.create(
            project=project1,
            version='1',
            date_added=datetime(2013, 8, 13, 3, 8, 24, 880386),
        )
        release2 = Release.objects.create(
            project=project1,
            version='2',
            date_added=datetime(2013, 8, 14, 3, 8, 24, 880386),
        )
        Release.objects.create(
            project=project2,
            version='1',
        )

        url = reverse('sentry-api-0-project-releases', kwargs={
            'organization_slug': project1.organization.slug,
            'project_slug': project1.slug,
        })
        response = self.client.get(url, format='json')

        assert response.status_code == 200, response.content
        assert len(response.data) == 2
        assert response.data[0]['version'] == release2.version
        assert response.data[1]['version'] == release1.version


class ProjectReleaseCreateTest(APITestCase):
    def test_simple(self):
        self.login_as(user=self.user)

        team = self.create_team(owner=self.user)
        project = self.create_project(team=team, name='foo')

        url = reverse('sentry-api-0-project-releases', kwargs={
            'organization_slug': project.organization.slug,
            'project_slug': project.slug,
        })
        response = self.client.post(url, data={
            'version': 'abcdef',
        })

        assert response.status_code == 201, response.content
        assert response.data['version']

        assert Release.objects.filter(
            project=project,
            version=response.data['version'],
        ).exists()
