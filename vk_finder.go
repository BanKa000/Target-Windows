package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/SevereCloud/vksdk/v3/api"
	"github.com/xuri/excelize/v2"
)

// VK API конфигурация
const (
	VK_API_VERSION = "5.199"
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
	fmt.Println("\n📋 Как получить токен:")
	fmt.Println("1. Откройте в браузере эту ссылку:")
	fmt.Println("   https://oauth.vk.com/authorize?client_id=2685278&scope=offline,groups&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&v=5.199")
	fmt.Println("\n2. Авторизуйтесь в ВКонтакте")
	fmt.Println("\n3. После авторизации вы попадёте на страницу с адресом вида:")
	fmt.Println("   https://oauth.vk.com/blank.html#access_token=ТОКЕН_ЗДЕСЬ&expires_in=0&user_id=ВАШ_ID")
	fmt.Println("\n4. Скопируйте значение access_token (длинная строка между access_token= и &)")
	fmt.Println("\n5. Вставьте его ниже:")
	fmt.Println("─────────────────────────────────────────")
	
	reader := bufio.NewReader(os.Stdin)
	fmt.Print("\nВведите токен доступа: ")
	token, _ := reader.ReadString('\n')
	token = strings.TrimSpace(token)
	
	if token == "" {
		fmt.Println("❌ Токен не введён")
		return false
	}

	accessToken = token
	return validateToken()
}

func validateToken() bool {
	params := url.Values{}
	params.Set("access_token", accessToken)
	params.Set("v", VK_API_VERSION)
	
	resp, err := http.Get("https://api.vk.com/method/users.get?" + params.Encode())
	if err != nil {
		fmt.Printf("❌ Ошибка подключения: %v\n", err)
		return false
	}
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("❌ Ошибка чтения ответа: %v\n", err)
		return false
	}
	
	// Парсим JSON ответ
	var result struct {
		Response []struct {
			ID        int    `json:"id"`
			FirstName string `json:"first_name"`
			LastName  string `json:"last_name"`
		} `json:"response"`
		Error *struct {
			ErrorCode int    `json:"error_code"`
			ErrorMsg  string `json:"error_msg"`
		} `json:"error"`
	}
	
	if err := json.Unmarshal(body, &result); err != nil {
		fmt.Printf("❌ Ошибка парсинга ответа: %v\n", err)
		fmt.Printf("Ответ сервера: %s\n", string(body))
		return false
	}
	
	// Проверяем наличие ошибки
	if result.Error != nil {
		fmt.Printf("❌ Ошибка VK API: %s\n", result.Error.ErrorMsg)
		fmt.Printf("Код ошибки: %d\n", result.Error.ErrorCode)
		return false
	}
	
	// Проверяем наличие данных
	if len(result.Response) == 0 {
		fmt.Printf("❌ Не удалось получить данные пользователя\n")
		return false
	}
	
	// Успех!
	user := result.Response[0]
	fmt.Printf("✅ Авторизация успешна!\n")
	fmt.Printf("Пользователь: %s %s (ID: %d)\n", user.FirstName, user.LastName, user.ID)
	return true
}
func searchCommunities() {
	reader := bufio.NewReader(os.Stdin)
	
	fmt.Print("\nВведите поисковый запрос: ")
	query, _ := reader.ReadString('\n')
	query = strings.TrimSpace(query)

	fmt.Print("Максимальное количество результатов (10-500): ")
	var maxResultsStr string
	maxResultsStr, _ = reader.ReadString('\n')
	maxResultsStr = strings.TrimSpace(maxResultsStr)
	
	maxResults := 50
	if n, err := strconv.Atoi(maxResultsStr); err == nil {
		if n < 10 {
			maxResults = 10
		} else if n > 500 {
			maxResults = 500
		} else {
			maxResults = n
		}
	}

	fmt.Println("\n⏳ Поиск сообществ...")

	// Используем библиотеку vksdk для API запросов
	vk := api.NewVK(accessToken)

	params := api.Params{
		"q":     query,
		"type":  "group",
		"count": maxResults,
	}

	// Используем прямой вызов API через Request
	resp, err := vk.Request("groups.search", params)
	if err != nil {
		fmt.Printf("❌ Ошибка VK API: %v\n", err)
		return
	}

	// Парсим ответ VK API
	var apiResponse struct {
		Response struct {
			Count int `json:"count"`
			Items []struct {
				ID          int    `json:"id"`
				Name        string `json:"name"`
				ScreenName  string `json:"screen_name"`
				Members     int    `json:"member_count"`
				Description string `json:"description"`
				Site        string `json:"site"`
			} `json:"items"`
		} `json:"response"`
		Error *struct {
			ErrorCode int    `json:"error_code"`
			ErrorMsg  string `json:"error_msg"`
		} `json:"error"`
	}

	if err := json.Unmarshal(resp, &apiResponse); err != nil {
		fmt.Printf("❌ Ошибка парсинга ответа: %v\n", err)
		return
	}

	// Проверяем наличие ошибки в ответе
	if apiResponse.Error != nil {
		fmt.Printf("❌ Ошибка VK API: %s\n", apiResponse.Error.ErrorMsg)
		return
	}

	result := apiResponse.Response

	fmt.Printf("\n✅ Найдено %d сообществ:\n\n", len(result.Items))

	// Конвертируем результаты в наш формат
	communities := make([]Community, len(result.Items))
	for i, group := range result.Items {
		communities[i] = Community{
			ID:          group.ID,
			Name:        group.Name,
			ScreenName:  group.ScreenName,
			Members:     group.Members,
			Description: group.Description,
			Site:        group.Site,
		}
	}

	for i, community := range communities {
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
	saveResults(communities)
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
