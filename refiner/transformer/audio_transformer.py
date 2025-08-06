from typing import Any
from refiner.transformer.base_transformer import DataTransformer
from refiner.models.refined import UserRefined, AudioRefined
from refiner.models.unrefined import Audio


class AudioTransformer(DataTransformer):
    def transform(self, data: dict[str, Any]):
        # Validate data with Pydantic
        unrefined_audio = Audio.model_validate(data)

        # Create user instance
        audio = AudioRefined(
            language_code=unrefined_audio.language_code,
            audio_length=unrefined_audio.audio_length,
            audio_type=unrefined_audio.audio_type,
            audio_source=unrefined_audio.audio_source,
            wallet_address=unrefined_audio.user.wallet_address,
            raw_data=unrefined_audio.raw_data,
        )

        models = [audio]

        user = UserRefined(
            wallet_address=unrefined_audio.user.wallet_address,
            birth_year=unrefined_audio.user.birth_year,
            birth_month=unrefined_audio.user.birth_month,
            occupation=unrefined_audio.user.occupation,
            country=unrefined_audio.user.country,
            region=unrefined_audio.user.region,
        )
        models.append(user)

        return models
