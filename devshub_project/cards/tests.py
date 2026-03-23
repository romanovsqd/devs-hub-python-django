from django.test import TestCase

from users import services as user_services

from . import services


class CardTest(TestCase):
    def setUp(self):
        self.user = user_services.create_user("user", "password123")

    def test_create_card(self):
        card = services.create_card(
            author=self.user,
            question="test card question",
            answer="test card answer",
        )

        self.assertEqual(card.author, self.user)
        self.assertEqual(card.question, "test card question")
        self.assertEqual(card.answer, "test card answer")

        self.assertEqual(services.get_cards().count(), 1)

        db_card = services.get_cards().first()
        self.assertEqual(card.id, db_card.id)

    def test_toggle_save_card(self):
        test_user = user_services.create_user("test_user", "password123")

        services.create_card(
            author=test_user,
            question="test card question",
            answer="test card answer",
        )

        card = services.get_cards_with_saved_status(user=self.user).first()
        is_saved, message = services.toggle_card_save_by_user(card=card, user=self.user)

        self.assertEqual(is_saved, True)
        self.assertEqual(message, "Карточка сохранена в ваш профиль")
        self.assertEqual(self.user.saved_cards.count(), 1)

        card = services.get_cards_with_saved_status(user=self.user).first()
        is_saved, message = services.toggle_card_save_by_user(card=card, user=self.user)

        self.assertEqual(is_saved, False)
        self.assertEqual(message, "Карточка удалена из вашего профиля")
        self.assertEqual(self.user.saved_cards.count(), 0)

    def test_toggle_save_own_card(self):
        test_user = user_services.create_user("test_user", "password123")

        services.create_card(
            author=test_user,
            question="test card question",
            answer="test card answer",
        )

        card = services.get_cards_with_saved_status(user=test_user).first()
        is_saved, message = services.toggle_card_save_by_user(card=card, user=test_user)

        self.assertEqual(is_saved, False)
        self.assertEqual(message, "Вы автор этой карточки")
        self.assertEqual(self.user.saved_cards.count(), 0)
