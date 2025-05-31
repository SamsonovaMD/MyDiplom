// src/utils/translations.js (New File or add to an existing utils file)
export const WORK_FORMAT_DISPLAY = {
  remote: 'Удаленно',
  hybrid: 'Гибрид',
  office: 'В офисе',
};

export const EMPLOYMENT_TYPE_DISPLAY = {
  full_time: 'Полная занятость',
  part_time: 'Частичная занятость',
  internship: 'Стажировка',
};

export const getWorkFormatDisplay = (value) => WORK_FORMAT_DISPLAY[value] || value;
export const getEmploymentTypeDisplay = (value) => EMPLOYMENT_TYPE_DISPLAY[value] || value;