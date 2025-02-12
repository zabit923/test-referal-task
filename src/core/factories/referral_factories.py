from datetime import datetime, timedelta

import factory
from faker import Faker

from core.database.models import Referral, ReferralCode
from core.factories import UserFactory

fake = Faker()


class ReferralCodeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ReferralCode

    owner = factory.SubFactory(UserFactory)
    code = factory.LazyAttribute(lambda _: fake.bothify(text="????####"))
    expires_at = factory.LazyAttribute(lambda _: datetime.now() + timedelta(days=7))
    is_active = True


class ReferralFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Referral

    referrer = factory.SubFactory(UserFactory)
    referred = factory.SubFactory(UserFactory)
