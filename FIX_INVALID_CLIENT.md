# Инструкция по исправлению ошибки "invalid_client" (обновлено)

## Проблема

Ошибка `invalid_client - client_secret is undefined` возникала из-за того, что VK теперь требует `client_secret` для Direct Auth (авторизации по логину/паролю).

## Решение

Программа теперь использует **OAuth Implicit Flow через браузер** - это стандартный и самый надёжный способ авторизации VK.

### Как это работает:

1. Программа открывает браузер с URL авторизации VK
2. Пользователь авторизуется любым способом (логин/пароль, QR-код, и т.д.)
3. После успешной авторизации VK перенаправляет на локальный сервер программы
4. Программа автоматически извлекает токен из URL
5. Токен сохраняется и используется для работы с API

### Преимущества:

✅ Работает с двухфакторной аутентификацией  
✅ Не требует client_secret  
✅ Не требует ввода пароля в программе  
✅ Стандартный механизм OAuth  
✅ Безопаснее - пароль не передаётся через программу

## Что было изменено

### 1. Импорты (vk_finder.go)

**Было:**
```go
import (
    "github.com/SevereCloud/vksdk/v3/api"
    "github.com/SevereCloud/vksdk/v3/oauth" // ❌ Пакет oauth также вынесен
    "github.com/xuri/excelize/v2"
)
```

**Стало:**
```go
import (
    "github.com/SevereCloud/vksdk/v3/api"
    "github.com/xuri/excelize/v2"
    // oauth пакет удалён, используется прямой HTTP-запрос
)
```

### 2. Функция авторизации (vk_finder.go)

**Было:**
```go
auth, err := oauth.DirectAuth(&oauth.Params{
    Login:        login,
    Password:     password,
    ClientID:     VK_APP_ID,
    ClientSecret: "",
    Scope:        api.ScopeOffline,
})
```

**Стало:**
```go
// Прямой HTTP-запрос для получения токена
func getVKToken(login, password, clientID string) (string, int64, error) {
    data := url.Values{
        "grant_type": {"password"},
        "client_id":  {clientID},
        "username":   {login},
        "password":   {password},
        "scope":      {"offline,friends,groups"},
        "v":          {VK_API_VERSION},
    }

    resp, err := http.PostForm("https://oauth.vk.com/token", data)
    // ... обработка ответа
    return tokenResp.AccessToken, tokenResp.UserID, nil
}

// Использование:
token, userID, err := getVKToken(login, password, fmt.Sprintf("%d", VK_APP_ID))
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

### 4. Вызов API для поиска сообществ (vk_finder.go)

**Было:**
```go
resp, err := vk.Groups.Search(params)
```

**Стало:**
```go
resp, err := vk.Request("groups.search", params)
// resp - это []byte, парсим через json.Unmarshal
var apiResponse struct {
    Response struct {
        Count int `json:"count"`
        Items []struct { ... } `json:"items"`
    } `json:"response"`
    Error *struct { ... } `json:"error"`
}
json.Unmarshal(resp, &apiResponse)
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
✅ **Прямой HTTP-запрос** - не зависит от сторонних пакетов oauth  
✅ **Полный контроль** - можно обрабатывать все ошибки и 2FA  
✅ **Нет ошибок "invalid_client"** - правильная реализация Direct Auth  
✅ **Прямой вызов API** - используется `vk.Request()` вместо устаревших методов  
✅ **Минимальные зависимости** - только api и excelize  

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
- **Метод авторизации**: OAuth Implicit Flow через браузер
- **App ID**: 2685278 (Kate Mobile) - может быть заблокирован VK
- **Client Secret**: не требуется
- **Метод поиска**: `vk.Request("groups.search", params)`
- **Функция авторизации**: `getVKTokenViaBrowser(clientID)`
- **Локальный сервер**: запускается на случайном порту для получения токена
- **Таймаут**: 5 минут на авторизацию

## Ошибка "incorrect app. Unavailable for apps with direct auth."

Если вы видите эту ошибку, VK заблокировал использование app_id для OAuth.

### Решения:

**1. Используйте альтернативные app_id для получения токена вручную:**

Откройте в браузере один из этих URL:

```
https://oauth.vk.com/authorize?client_id=5157339&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

```
https://oauth.vk.com/authorize?client_id=3697615&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

```
https://oauth.vk.com/authorize?client_id=6121269&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

После авторизации скопируйте токен из URL и вставьте в программу (опция "2").

**2. Создайте собственное приложение в VK:**

1. Перейдите на https://dev.vk.com/ru/admin/apps-list
2. Создайте новое приложение (тип: "Веб-сайт" или "Standalone")
3. Получите app_id вашего приложения
4. Измените константу `VK_APP_ID` в файле `vk_finder.go`
5. Пересоберите программу: `go build -o vk_finder.exe vk_finder.go`

## Документация

- [README.md](README.md) - полная документация
- [START_HERE.md](START_HERE.md) - краткая инструкция

---

**Дата исправления**: 2026  
**Версия**: 1.5 (добавлены альтернативные app_id и инструкция по созданию приложения)

## Быстрое решение

Если видите ошибку "incorrect app", используйте один из этих URL для получения токена вручную:

```
https://oauth.vk.com/authorize?client_id=5157339&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

```
https://oauth.vk.com/authorize?client_id=3697615&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

```
https://oauth.vk.com/authorize?client_id=6121269&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token
```

После авторизации скопируйте токен из URL и вставьте в программу (опция "2").
