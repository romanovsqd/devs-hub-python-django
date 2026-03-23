from django.db import IntegrityError
from django.test import TestCase

from users import services as user_services

from . import services


class ProjectTest(TestCase):
    def setUp(self):
        self.user = user_services.create_user("user", "password123")

    def test_create_project(self):
        project = services.create_project(
            author=self.user,
            title="test project title",
            description="test project description",
        )

        self.assertEqual(project.author, self.user)
        self.assertEqual(project.title, "test project title")
        self.assertEqual(project.description, "test project description")

        self.assertEqual(services.get_projects().count(), 1)

        db_project = services.get_projects().first()
        self.assertEqual(project.id, db_project.id)

    def test_create_project_without_author(self):
        with self.assertRaises((IntegrityError)):
            services.create_project(
                author=None,
                title="test project title",
                description="test project description",
            )
