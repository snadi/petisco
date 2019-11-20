def sqlalchemy_extension_is_installed() -> bool:
    try:
        import sqlalchemy  # noqa: F401

        return True
    except:  # noqa: E722
        return False
