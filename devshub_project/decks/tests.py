from django.http import Http404
from django.test import TestCase

from cards.models import Card
from users import services as user_services

from . import services


class DeckTest(TestCase):
    def setUp(self):
        self.user = user_services.create_user("user", "password123")

        cards = [
            Card(author=self.user, question="test", answer="test") for i in range(3)
        ]
        self.cards = Card.objects.bulk_create(cards)

    def test_create_deck(self):
        deck = services.create_deck(
            author=self.user,
            title="test deck title",
            cards=self.cards,
        )

        self.assertEqual(deck.author, self.user)
        self.assertEqual(deck.title, "test deck title")
        self.assertEqual(deck.cards.count(), 3)
        self.assertEqual(services.get_decks().count(), 1)

        db_deck = services.get_decks().first()
        self.assertEqual(deck.id, db_deck.id)

    def test_toggle_save_deck(self):
        test_user = user_services.create_user("test_user", "password123")

        services.create_deck(
            author=test_user,
            title="test deck title",
            cards=self.cards,
        )

        deck = services.get_decks_with_saved_status(user=self.user).first()
        is_saved, message = services.toggle_deck_save_by_user(deck=deck, user=self.user)

        self.assertEqual(is_saved, True)
        self.assertEqual(message, "Колода сохранена в ваш профиль")
        self.assertEqual(self.user.saved_decks.count(), 1)

        deck = services.get_decks_with_saved_status(user=self.user).first()
        is_saved, message = services.toggle_deck_save_by_user(deck=deck, user=self.user)

        self.assertEqual(is_saved, False)
        self.assertEqual(message, "Колода удалена из вашего профиля")
        self.assertEqual(self.user.saved_decks.count(), 0)

    def test_toggle_save_own_deck(self):
        test_user = user_services.create_user("test_user", "password123")

        services.create_deck(
            author=test_user,
            title="test deck title",
            cards=self.cards,
        )

        deck = services.get_decks_with_saved_status(user=test_user).first()
        is_saved, message = services.toggle_deck_save_by_user(deck=deck, user=test_user)

        self.assertEqual(is_saved, False)
        self.assertEqual(message, "Вы автор этой колоды")
        self.assertEqual(self.user.saved_decks.count(), 0)

    def test_toggle_study_deck(self):
        test_user = user_services.create_user("test_user", "password123")

        new_deck = services.create_deck(
            author=test_user,
            title="test deck title",
            cards=self.cards,
        )

        deck = services.get_deck_created_or_saved_by_user(
            deck_id=new_deck.pk, user=test_user
        )
        is_study, message = services.toggle_deck_study_by_user(
            deck=deck, user=test_user
        )

        self.assertEqual(is_study, True)
        self.assertEqual(message, f"Вы изучаете колоду {deck.title}")

        is_study, message = services.toggle_deck_study_by_user(
            deck=deck, user=test_user
        )

        self.assertEqual(is_study, False)
        self.assertEqual(message, f"Сброшен весь прогресс по колоде {deck.title}")

    def test_toggle_study_unsaved_deck(self):
        test_user = user_services.create_user("test_user", "password123")

        services.create_deck(
            author=test_user,
            title="test deck title",
            cards=self.cards,
        )

        with self.assertRaises(Http404):
            services.get_deck_created_or_saved_by_user(deck_id=1, user=self.user)
