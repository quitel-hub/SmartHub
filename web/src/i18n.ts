export type Language = 'ukr' | 'eng';

export const translations = {
  ukr: {
    header: {
      version: 'v2.0 Full-stack',
      live: 'Render Live',
      title: 'SmartHub',
      subtitle: ' Workspace',
      desc: 'Аналітична панель розпізнавання студентських конспектів',
      sync: 'Синхронізувати',
    },
    metrics: {
      dbTitle: 'База знань',
      dbCount: 'документів',
      dbFootnote: 'Автоматична класифікація макетів',
      speedTitle: 'Прискорення рушія',
      speedCount: 'оптимізація',
      speedFootnote: 'Багатопотоковий пул (4 threads)',
      benchTitle: 'OCR Час обробки (Пакет 20 фото)',
      benchBadge: 'Тест',
      seq: '1 потік (Послідовно)',
      par: '4 потоки (Паралельно)',
    },
    search: {
      placeholder: 'Пошук за контентом чи автором...',
      all: 'Усі',
    },
    cards: {
      recent: 'Нещодавно',
      save: 'Зберегти',
      emptyContent: 'Порожній контент',
      student: 'Студент:',
      anon: 'Анонім',
      tabOrig: 'Оригінал',
      tabTrans: 'Переклад',
    },
    states: {
      loading: 'Завантаження даних з бекенду...',
      notFound: 'Конспектів не знайдено',
      notFoundSub: 'Спробуй змінити критерії пошуку',
    }
  },
  eng: {
    header: {
      version: 'v2.0 Full-stack',
      live: 'Render Live',
      title: 'SmartHub',
      subtitle: ' Workspace',
      desc: 'Analytical dashboard for student notes recognition',
      sync: 'Synchronize',
    },
    metrics: {
      dbTitle: 'Knowledge Base',
      dbCount: 'documents',
      dbFootnote: 'Automatic layout classification',
      speedTitle: 'Engine Acceleration',
      speedCount: 'optimization',
      speedFootnote: 'Multi-threaded pool (4 threads)',
      benchTitle: 'OCR Processing Time (20 photos)',
      benchBadge: 'Test',
      seq: '1 thread (Sequential)',
      par: '4 threads (Parallel)',
    },
    search: {
      placeholder: 'Search by content or author...',
      all: 'All',
    },
    cards: {
      recent: 'Recently',
      save: 'Save',
      emptyContent: 'Empty content',
      student: 'Student:',
      anon: 'Anonymous',
      tabOrig: 'Original',
      tabTrans: 'Translation',
    },
    states: {
      loading: 'Loading data from backend...',
      notFound: 'No notes found',
      notFoundSub: 'Try changing your search criteria',
    }
  }
};