from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class ListingRateThrottle(AnonRateThrottle):
    scope = "listing"


class LoginRateThrottle(AnonRateThrottle):
    scope = "login"


class RegistrationRateThrottle(AnonRateThrottle):
    scope = "registration"


class ConsultaCreateRateThrottle(UserRateThrottle):
    scope = "consulta_create"


class ProfissionalCreateRateThrottle(UserRateThrottle):
    scope = "profissional_create"


class SensitiveDataRateThrottle(UserRateThrottle):
    scope = "sensitive_data"
