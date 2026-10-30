from app.core.config import Settings


def test_normaliza_url_neon_para_psycopg3() -> None:
    url = "postgresql://usuario:clave@ep-example.neon.tech/fletes?sslmode=require"

    settings = Settings(DATABASE_URL=url)

    assert (
        settings.DATABASE_URL
        == "postgresql+psycopg://usuario:clave@ep-example.neon.tech/fletes?sslmode=require"
    )


def test_conserva_url_que_ya_declara_psycopg3() -> None:
    url = "postgresql+psycopg://usuario:clave@localhost/fletes"

    settings = Settings(DATABASE_URL=url)

    assert settings.DATABASE_URL == url
