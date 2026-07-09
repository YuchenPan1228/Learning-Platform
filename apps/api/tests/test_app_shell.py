def test_create_app() -> None:
    from app.main import create_app

    application = create_app()
    assert application.title == "Quant Prep API"
