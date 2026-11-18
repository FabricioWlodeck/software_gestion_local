"""Repositories: el acceso a los datos con SQLAlchemy. No validan reglas ni confirman cambios."""

from datetime import date, datetime, time, timedelta


def rango_de_fechas(desde: date | None, hasta: date | None) -> tuple[datetime | None, datetime | None]:
    """Fechas inclusivas → [desde 00:00, hasta+1 00:00). Así se puede usar el índice por fecha."""
    inicio = datetime.combine(desde, time.min) if desde else None
    fin = datetime.combine(hasta + timedelta(days=1), time.min) if hasta else None
    return inicio, fin
