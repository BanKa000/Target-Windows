package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"regexp"
	"strings"
	"time"

	"github.com/xuri/excelize/v2"
)

// VK API конфигурация
const (
	VK_API_VERSION = "5.199"
	VK_APP_ID      = "2274003" // VK для Android (официальное приложение)
)

// Структуры данных
type Community struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	ScreenName  string `json:"screen_name"`
	Members     int    `json:"members_count"`
	Description string `json:"description"`
	Site        string `json:"site"`
	Phone       string
	Email       string
	City        string
	Verified    bool
}

type VKResponse struct {
	Response struct {
		Count int         `json:"count"`
		Items []Community `json:"items"`
	} `json:"response"`
	Error *struct {
		ErrorCode int    `json:"error_code"`
		ErrorMsg  string `json:"error_msg"`
	} `json:"error"`
}

// Глобальные переменные
var accessToken string

func main() {
	fmt.Println("==========================================")
	fmt.Println("  VK Community Finder на Go")
	fmt.Println("==========================================")
	fmt.Println()

	// Авторизация
	if !login() {
		fmt.Println("Не удалось авторизоваться. Завершение.")
		return
	}

	// Основной цикл
	for {
		fmt.Println("\nЧто вы хотите сделать?")
		fmt.Println("1. Поиск сообществ")
		fmt.Println("2. Экспорт в Excel")
		fmt.Println("3. Выход")
		fmt.Print("Выберите действие (1-3): ")

		var choice string
		fmt.Scanln(&choice)

		switch choice {
		case "1":
			searchCommunities()
		case "2":
			exportToExcel()
		case "3":
			fmt.Println("До свидания!")
			return
		default:
			fmt.Println("Неверный выбор. Попробуйте снова.")
		}
	}
}

func login() bool {
	fmt.Println("\n--- Авторизация ВКонтакте ---")
	fmt.Println("1. Войти по логину/паролю")
	fmt.Println("2. Использовать существующий токен")
	fmt.Print("Выберите (1-2): ")

	var choice string
	fmt.Scanln(&choice)

	if choice == "2" {
		fmt.Print("Введите токен доступа: ")
		fmt.Scanln(&accessToken)
		return validateToken()
	}

	fmt.Print("Логин (телефон или email): ")
	var login string
	fmt.Scanln(&login)

	fmt.Print("Пароль: ")
	var password string
	fmt.Scanln(&password)

	// Direct Auth через официальное приложение VK
	params := url.Values{}
	params.Set("client_id", VK_APP_ID)
	params.Set("username", login)
	params.Set("password", password)
	params.Set("v", VK_API_VERSION)
	params.Set("2fa_supported", "1")
	params.Set("scope", "offline")

	resp, err := http.PostForm("https://oauth.vk.com/token", params)
	if err != nil {
		fmt.Printf("Ошибка подключения: %v\n", err)
		return false
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	var result struct {
		AccessToken string `json:"access_token"`
		Error       string `json:"error"`
		ErrorDesc   string `json:"error_description"`
		NeedCaptcha bool   `json:"need_captcha"`
		CaptchaSid  string `json:"captcha_sid"`
		ValidationSid string `json:"validation_sid"`
		PhoneMask   string `json:"phone_mask"`
		RedirectUri string `json:"redirect_uri"`
	}

	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("Ошибка парсинга ответа: %v\n", err)
		return false
	}

	// Обработка 2FA
	if result.ValidationSid != "" {
		fmt.Println("\n⚠️  Требуется двухфакторная авторизация")
		fmt.Print("Введите код из приложения VK: ")
		var code string
		fmt.Scanln(&code)

		// Повторная попытка с кодом
		params.Set("code", code)
		resp2, err := http.PostForm("https://oauth.vk.com/token", params)
		if err != nil {
			fmt.Printf("Ошибка подключения: %v\n", err)
			return false
		}
		defer resp2.Body.Close()

		body2, _ := io.ReadAll(resp2.Body)
		if err := json.Unmarshal(body2, &result); err != nil {
			fmt.Printf("Ошибка парсинга ответа: %v\n", err)
			return false
		}
	}

	if result.Error != "" {
		fmt.Printf("Ошибка авторизации: %s - %s\n", result.Error, result.ErrorDesc)
		if result.NeedCaptcha {
			fmt.Println("VK запрашивает капчу. Попробуйте позже или используйте токен.")
		}
		if result.ValidationSid != "" {
			fmt.Println("Неверный код 2FA. Попробуйте снова.")
		}
		return false
	}

	accessToken = result.AccessToken
	fmt.Println("✅ Авторизация успешна!")
	return true
}

func validateToken() bool {
	params := url.Values{}
	params.Set("access_token", accessToken)
	params.Set("v", VK_API_VERSION)

	resp, err := http.Get("https://api.vk.com/method/users.get?" + params.Encode())
	if err != nil {
		fmt.Printf("Ошибка: %v\n", err)
		return false
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	return !strings.Contains(string(body), "error")
}

func searchCommunities() {
	fmt.Print("\nВведите поисковый запрос: ")
	var query string
	fmt.Scanln(&query)

	fmt.Print("Максимальное количество результатов (10-500): ")
	var maxResults int
	fmt.Scanln(&maxResults)

	if maxResults < 10 {
		maxResults = 10
	}
	if maxResults > 500 {
		maxResults = 500
	}

	fmt.Println("\nПоиск сообществ...")

	params := url.Values{}
	params.Set("access_token", accessToken)
	params.Set("q", query)
	params.Set("type", "group")
	params.Set("count", fmt.Sprintf("%d", maxResults))
	params.Set("v", VK_API_VERSION)

	resp, err := http.Get("https://api.vk.com/method/groups.search?" + params.Encode())
	if err != nil {
		fmt.Printf("Ошибка: %v\n", err)
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)

	var vkResp VKResponse
	if err := json.Unmarshal(body, &vkResp); err != nil {
		fmt.Printf("Ошибка парсинга: %v\n", err)
		return
	}

	if vkResp.Error != nil {
		fmt.Printf("Ошибка VK API: %s\n", vkResp.Error.ErrorMsg)
		return
	}

	fmt.Printf("\nНайдено %d сообществ:\n\n", len(vkResp.Response.Items))

	for i, community := range vkResp.Response.Items {
		fmt.Printf("%d. %s\n", i+1, community.Name)
		fmt.Printf("   URL: https://vk.com/%s\n", community.ScreenName)
		fmt.Printf("   Участников: %d\n", community.Members)
		if community.Description != "" {
			desc := community.Description
			if len(desc) > 100 {
				desc = desc[:100] + "..."
			}
			fmt.Printf("   Описание: %s\n", desc)
		}
		fmt.Println()
	}

	// Сохраняем результаты для экспорта
	saveResults(vkResp.Response.Items)
}

var lastResults []Community

func saveResults(communities []Community) {
	lastResults = communities
	fmt.Printf("Результаты сохранены. Используйте 'Экспорт в Excel' для сохранения в файл.\n")
}

func exportToExcel() {
	if len(lastResults) == 0 {
		fmt.Println("Нет данных для экспорта. Сначала выполните поиск.")
		return
	}

	filename := fmt.Sprintf("vk_communities_%s.xlsx", time.Now().Format("2006-01-02"))

	f := excelize.NewFile()
	sheet := "Сообщества"
	index, _ := f.NewSheet(sheet)
	f.SetActiveSheet(index)

	// Заголовки
	headers := []string{"№", "Название", "Ссылка", "Участники", "Описание", "Сайт", "Телефон", "Email", "Город"}
	
	// Создаём стиль для заголовков
	styleID, err := f.NewStyle(&excelize.Style{
		Font: &excelize.Font{Bold: true, Color: "#FFFFFF"},
		Fill: excelize.Fill{Type: "pattern", Pattern: 1, Color: []string{"#4C75A3"}},
	})
	if err != nil {
		fmt.Printf("Ошибка создания стиля: %v\n", err)
		return
	}
	
	for i, header := range headers {
		cell := fmt.Sprintf("%c1", 'A'+i)
		f.SetCellValue(sheet, cell, header)
		f.SetCellStyle(sheet, cell, cell, styleID)
	}

	// Данные
	for i, community := range lastResults {
		row := i + 2
		f.SetCellValue(sheet, fmt.Sprintf("A%d", row), i+1)
		f.SetCellValue(sheet, fmt.Sprintf("B%d", row), community.Name)
		f.SetCellValue(sheet, fmt.Sprintf("C%d", row), fmt.Sprintf("https://vk.com/%s", community.ScreenName))
		f.SetCellValue(sheet, fmt.Sprintf("D%d", row), community.Members)
		f.SetCellValue(sheet, fmt.Sprintf("E%d", row), community.Description)
		f.SetCellValue(sheet, fmt.Sprintf("F%d", row), community.Site)
		f.SetCellValue(sheet, fmt.Sprintf("G%d", row), community.Phone)
		f.SetCellValue(sheet, fmt.Sprintf("H%d", row), community.Email)
		f.SetCellValue(sheet, fmt.Sprintf("I%d", row), community.City)
	}

	// Ширина колонок
	f.SetColWidth(sheet, "A", "A", 5)
	f.SetColWidth(sheet, "B", "B", 40)
	f.SetColWidth(sheet, "C", "C", 35)
	f.SetColWidth(sheet, "D", "D", 12)
	f.SetColWidth(sheet, "E", "E", 50)
	f.SetColWidth(sheet, "F", "F", 30)
	f.SetColWidth(sheet, "G", "G", 18)
	f.SetColWidth(sheet, "H", "H", 25)
	f.SetColWidth(sheet, "I", "I", 15)

	if err := f.SaveAs(filename); err != nil {
		fmt.Printf("Ошибка сохранения: %v\n", err)
		return
	}

	fmt.Printf("✅ Файл сохранён: %s\n", filename)
}

// Удаление HTML тегов
func stripHTML(text string) string {
	re := regexp.MustCompile(`<[^>]*>`)
	return re.ReplaceAllString(text, "")
}
