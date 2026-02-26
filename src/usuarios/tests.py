from django.contrib.auth import get_user_model
from django.test import TestCase


class PerfilUsuarioTests(TestCase):
    def test_crea_perfil_automaticamente(self):
        user = get_user_model().objects.create_user(username="owner", password="pass1234")
        self.assertTrue(hasattr(user, "perfil"))