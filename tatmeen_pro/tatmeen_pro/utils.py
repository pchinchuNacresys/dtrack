import uuid
import random
import string
from django.db import transaction
from material_inward.models import *

def generate_random_string_with_uuid_seed(length=40):
    seed = uuid.uuid4().int  # Get a big integer from UUID
    random.seed(seed)  # Seed the random generator
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))


def get_next_serials(key, count=1):
    with transaction.atomic():
        tracker, _ = SerialTracker.objects.select_for_update().get_or_create(key=key)
        start = tracker.last_serial + 1
        tracker.last_serial += count
        tracker.save()
        return [str(i).zfill(4) for i in range(start, start + count)]

