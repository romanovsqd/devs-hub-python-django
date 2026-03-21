import json

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from repetitions import services


class NextCard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        card_data = services.get_next_card_for_review(user=request.user)

        if card_data:
            return Response(card_data)
        else:
            return Response({"done": True})


class Submit(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, deck_id, card_id):
        data = request.data

        quality = int(data.get("quality", 0))

        card_progress = services.get_deck_card_progress_for_user(
            deck_id=deck_id,
            card_id=card_id,
            user=request.user,
        )

        progress = services.apply_sm2(progress=card_progress, quality=quality)

        return Response(
            {
                "deck_id": deck_id,
                "card_id": card_id,
                "next_review_date": progress.next_review_date.isoformat(),
                "interval": progress.interval,
                "efactor": progress.efactor,
                "repetitions": progress.repetitions,
            }
        )
