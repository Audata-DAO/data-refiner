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
            audio_length=unrefined_audio.audio_length,
            audio_type=unrefined_audio.audio_type,
            audio_source=unrefined_audio.audio_source,
            user_id=unrefined_audio.user.user_id,
        )

        models = [audio]

        user = UserRefined(
            user_id=unrefined_audio.user.user_id,
            age=unrefined_audio.user.age,
            country_code=unrefined_audio.user.country_code,
            occupation=unrefined_audio.user.occupation,
            language_code=unrefined_audio.user.language_code,
            region=unrefined_audio.user.region,
        )
        models.append(user)

        return models
