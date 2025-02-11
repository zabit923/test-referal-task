from sqladmin import ModelView

from core.database.models import Referral, ReferralCode


class RefferalCodeAdmin(ModelView, model=ReferralCode):
    column_list = [ReferralCode.id, ReferralCode.owner, ReferralCode.expires_at]
    column_searchable_list = [ReferralCode.code]
    column_default_sort = [("created_at", True)]
    name = "Реферальный код"
    name_plural = "Реферальные коды"
    icon = "fa-solid fa-user-plus"


class RefferalAdmin(ModelView, model=Referral):
    column_list = [Referral.id, Referral.referrer, Referral.referred]
    column_searchable_list = [Referral.id]
    name = "Реферал"
    name_plural = "Рефералы"
    icon = "fa-solid fa-link"
