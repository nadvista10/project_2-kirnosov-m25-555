from __future__ import annotations

from functools import wraps


def confirm_action(action_name: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(
                f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            ).strip().lower()
            if answer != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def handle_db_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
            return None
        except FileExistsError as e:
            print(f"Ошибка: {e}")
            return None
        except PermissionError as e:
            print(f"Ошибка доступа: {e}")
            return None
        except KeyError as e:
            message = str(e.args[0]) if getattr(e, "args", None) else str(e)
            print(f"Ошибка: {message}")
            return None
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
            return None
        except TypeError as e:
            print(f"Ошибка типа данных: {e}")
            return None
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
            return None

    return wrapper
