import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { Community } from '../types';

export function exportToExcel(communities: Community[], filename?: string) {
  const data = communities.map((community, index) => ({
    '№': index + 1,
    'ID': community.id,
    'Название': community.name,
    'Ссылка': `https://vk.com/${community.screen_name}`,
    'Тип': community.type === 'group' ? 'Группа' : community.type === 'page' ? 'Публичная страница' : 'Встреча',
    'Описание': community.description.replace(/<[^>]*>/g, '').substring(0, 500),
    'Участники': community.members_count,
    'Город': community.city?.title || '',
    'Сайт': community.site || '',
    'Телефон': community.phone || '',
    'Email': community.email || '',
    'Статус': community.status || '',
    'Активность': community.activity || '',
    'Верифицировано': community.verified ? 'Да' : 'Нет',
    'Закрытое': community.is_closed === 1 ? 'Да' : community.is_closed === 2 ? 'Частное' : 'Нет',
    'Дата сбора': new Date().toLocaleDateString('ru-RU'),
  }));

  const worksheet = XLSX.utils.json_to_sheet(data);
  
  // Ширина столбцов
  const colWidths = [
    { wch: 5 },   // №
    { wch: 10 },  // ID
    { wch: 30 },  // Название
    { wch: 35 },  // Ссылка
    { wch: 15 },  // Тип
    { wch: 50 },  // Описание
    { wch: 10 },  // Участники
    { wch: 15 },  // Город
    { wch: 30 },  // Сайт
    { wch: 18 },  // Телефон
    { wch: 25 },  // Email
    { wch: 30 },  // Статус
    { wch: 30 },  // Активность
    { wch: 12 },  // Верифицировано
    { wch: 10 },  // Закрытое
    { wch: 12 },  // Дата сбора
  ];
  worksheet['!cols'] = colWidths;

  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Сообщества');

  // Добавляем лист сводки
  const summaryData = [
    { 'Параметр': 'Всего сообществ', 'Значение': communities.length },
    { 'Параметр': 'Дата экспорта', 'Значение': new Date().toLocaleString('ru-RU') },
    { 'Параметр': 'С телефонами', 'Значение': communities.filter(c => c.phone).length },
    { 'Параметр': 'С сайтами', 'Значение': communities.filter(c => c.site).length },
    { 'Параметр': 'С email', 'Значение': communities.filter(c => c.email).length },
    { 'Параметр': 'Верифицированные', 'Значение': communities.filter(c => c.verified).length },
    { 'Параметр': 'Общее число участников', 'Значение': communities.reduce((sum, c) => sum + c.members_count, 0) },
  ];
  
  const summarySheet = XLSX.utils.json_to_sheet(summaryData);
  summarySheet['!cols'] = [{ wch: 25 }, { wch: 20 }];
  XLSX.utils.book_append_sheet(workbook, summarySheet, 'Сводка');

  const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  
  const exportFilename = filename || `vk_communities_${new Date().toISOString().slice(0, 10)}.xlsx`;
  saveAs(blob, exportFilename);
}
