# Web | Мышиные заметки

## Информация

> Мышъ любит сохранять заметки:
> <http://ip>

## Деплой

docker-compose в директории depoly/

## Выдать участникам

None

## Описание

Disclosure секретного ключа, LFI с SSTI

## Решение

1. Находим /old_login, со сломанным скриптом, который тянет секретный ключ и подписывает login из формы.
2. Достаем ключ (или фиксим скрипт), чтобы можно было создать куку-jwt для пользователя admin.
3. Заходим в админку, находим в ней SSTI.
4. Через SSTI достаем флаг по пути `/v3ry_l0ng_4nd_ungessable_nam3_du3_t0_that_you_need_RCE.txt`

## Флаг

`CUP{n0_m0r3_jinja_in_m0us3_lif3}`
