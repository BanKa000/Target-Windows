# Инструкция по исправлению ошибки "invalid_client"

## Проблема

Ошибка `invalid_client - client_secret is undefined` возникала из-за использования несуществующего пакета `github.com/SevereCloud/vksdk/v3/auth`.

## Решение

Исправлен код авторизации для использования правильного метода `vksdk.DirectAuth` из библиотеки vksdk/v3.

## Что было изменено

### 1. Импорты (vk_finder.go)

**Было:**
```go
import (
    "github.com/SevereCloud/vksdk/v3/api"
    "github.com/SevereCloud/vksdk/v3/auth"  // ❌ Несуществующий пакет
    "github.com/xuri/excelize/v2"
)
```

**Стало:**
```go
import (
    "github.com/SevereCloud/vksdk/v3"       // ✅ Правильный импорт
    "github.com/SevereCloud/vksdk/v3/api"
    "github.com/xuri/excelize/v2"
)
```

### 2. Функция авторизации (vk_finder.go)

**Было:**
```go
client := auth.NewClient(VK_APP_ID)
token, err := client.Login(login, password)
```

**Стало:**
```go
token, err := vksdk.DirectAuth(&vksdk.DirectAuthParams{
    Login:        login,
    Password:     password,
    ClientID:     VK_APP_ID,
    ClientSecret: "", // Для официальных приложений VK не требуется
    Scope:        api.ScopeOffline,
})
```

### 3. Тип VK_APP_ID (vk_finder.go)

**Было:**
```go
VK_APP_ID = "2274003" // Строка
```

**Стало:**
```go
VK_APP_ID = 2274003 // Число (int)
```

## Как использовать

### 1. Переустановите зависимости

```bash
install_go.bat
```

Этот скрипт выполнит:
- `go mod tidy` - синхронизация зависимостей
- `go mod download` - загрузка библиотек
- `go build` - сборка программы

### 2. Запустите программу

```bash
run_go.bat
```

### 3. Авторизация

Выберите **"1. Войти по логину/паролю"** и введите:
- Телефон или email
- Пароль

Программа использует `vksdk.DirectAuth` с официальным приложением VK для Android (app_id=2274003), что не требует client_secret.

## Преимущества нового метода

✅ **Не требует client_secret** - используется официальное приложение VK  
✅ **Автоматическая обработка 2FA** - библиотека сама запрашивает код  
✅ **Правильная работа с VK API** - используется официальный метод из vksdk  
✅ **Нет ошибок "invalid_client"** - правильная реализация Direct Auth  

## Если возникли проблемы

### Ошибка "package auth does not exist"

Убедитесь, что выполнили `install_go.bat` для переустановки зависимостей.

### Ошибка "invalid_client"

Проверьте, что в коде используется `vksdk.DirectAuth`, а не `auth.NewClient`.

### Ошибка компиляции

Выполните:
```bash
go mod tidy
go build -o vk_finder.exe vk_finder.go
```

## Технические детали

- **Библиотека**: github.com/SevereCloud/vksdk/v3 v3.0.0
- **Метод авторизации**: `vksdk.DirectAuth`
- **App ID**: 2274003 (VK для Android)
- **Client Secret**: не требуется для официальных приложений

## Документация

- [README.md](README.md) - полная документация
- [START_HERE.md](START_HERE.md) - краткая инструкция

---

**Дата исправления**: 2026  
**Версия**: 1.1 (исправлена ошибка invalid_client)
