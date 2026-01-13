# Primitive DB

Учебная файловая «мини-СУБД» на Python: таблицы и данные хранятся в JSON, управление - через интерактивный CLI.

## Быстрый старт

Требуется Python 3.12+ и Poetry.

```bash
make install
make project
```

Альтернатива без Makefile:

```bash
poetry install
poetry run project
```

## Как устроено хранение

- `data/metadata.json` - схема таблиц (названия столбцов и типы)
- `data/<table>.json` - данные таблицы
- Типы столбцов: `int`, `str`, `bool`
- Служебный столбец `__ID` создаётся автоматически

## Команды (синтаксис)

Команды вводятся в интерактивном режиме.

### create_table

```text
create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...
```

Пример:

```text
create_table users age:int name:str active:bool
```

### list_tables

```text
list_tables
```

### insert

```text
insert into <имя_таблицы> values (<значение1>, <значение2>, ...)
```

Пример:

```text
insert into users values (50, "some string value", True)
```

### select

```text
select from <имя_таблицы> [where <столбец>=<значение> where ...]
```

Примеры:

```text
select from users
select from users where __ID=1
select from users where age=50 where active=True
select from users where name="some string value"
```

### update

```text
update <имя_таблицы> set <столбец>=<значение> [set ...] where <столбец>=<значение> [where ...]
```

Пример:

```text
update users set age=21 set name="Some str" where __ID=3
```

Ограничение: `__ID` обновлять нельзя.

### delete

```text
delete from <имя_таблицы> where <столбец>=<значение> [where ...]
```

Пример:

```text
delete from users where active=False
```

### drop_table

```text
drop_table <имя_таблицы>
```

### help / exit

```text
help
exit
```

## Значения и кавычки

- Строки с пробелами указывайте в кавычках: `"some string value"`
- `bool`: `True/False` (также поддерживаются `1/0`)
- `int`: `123`

## Дополнительные возможности

### Централизованная обработка ошибок

Ошибки из DB-логики обрабатываются декоратором `handle_db_errors` (без падения программы)

### Подтверждение опасных действий

Для удаления таблицы и удаления записей используется декоратор `confirm_action(...)`.
Перед выполнением будет вопрос:

```text
Вы уверены, что хотите выполнить "удаление таблицы"? [y/n]:
```

Если ответ не `y`, операция отменяется.

### Замер времени выполнения

Декоратор `log_time` выводит время выполнения файловых операций в core:

```text
Функция select выполнилась за 0.012 секунд.
```

### Кэширование select

Повторяющиеся `select` с теми же параметрами могут брать значение из кэша через замыкание
После любых операций изменения (`create_table/insert/update/delete/drop_table`) кэш сбрасывается

## Структура проекта

- `src/primitive_db/engine.py` - CLI и разбор команд
- `src/primitive_db/core.py` - логика
- `src/primitive_db/utils.py` - чтение/запись JSON
- `src/decorators.py` - декораторы и замыкания
- `src/primitive_db/main.py` - точка входа

[![asciicast](https://asciinema.org/a/4bbWXvd17SVdDh5I.svg)](https://asciinema.org/a/4bbWXvd17SVdDh5I)
