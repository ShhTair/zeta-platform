# 🤖 AI Validation Guide

## Что это?

Система AI валидации использует OpenAI GPT-4o-mini для анализа продуктов в таблице и предоставления умных рекомендаций.

## ⚡ Быстрый старт

### 1. Настроен тестовый токен

OpenAI API ключ уже настроен в `.env.local`:

```bash
OPENAI_API_KEY=sk-proj-ZPMf...QXMA
```

### 2. Запустите приложение

```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/web
npm run dev
```

### 3. Тестовая страница

Откройте: **http://localhost:3000/test-ai**

Здесь можно:
- Ввести данные тестового продукта
- Нажать "Validate Product"
- Увидеть AI рекомендации в реальном времени

### 4. В таблице продуктов

Откройте: **http://localhost:3000/products**

1. Включите AI валидацию (кнопка "🤖 AI OFF" → "🤖 AI ON")
2. Отредактируйте любой продукт
3. Через 1 секунду появится иконка 🤖 если есть рекомендации
4. Наведите на иконку, чтобы увидеть подсказки

## 📊 Что проверяет AI?

### 1. Название продукта
- Слишком короткое или длинное
- Опечатки и грамматические ошибки
- Отсутствие ключевых характеристик
- Непрофессиональный стиль

**Пример:**
```
❌ "Mous"
✅ "Wireless Gaming Mouse with RGB Lighting"

AI suggestion: "Product name is too short. Add brand, key features, 
and specifications to make it more descriptive and searchable."
```

### 2. Описание
- Недостаточно деталей
- Отсутствие технических характеристик
- Нет информации о преимуществах
- Грамматические ошибки

**Пример:**
```
❌ "Small"
✅ "Ergonomic wireless mouse with 2.4GHz connectivity, 
6 programmable buttons, and up to 12-month battery life. 
Perfect for productivity and gaming."

AI suggestion: "Description is too brief. Include features, 
benefits, technical specs, and use cases."
```

### 3. Категория
- Неправильная категория для товара
- Альтернативные, более подходящие категории
- Стандартизация названий категорий

**Пример:**
```
❌ Category: "Food" for mouse
✅ Category: "Electronics" or "Computer Accessories"

AI suggestion: "Based on the product name containing 'mouse', 
this should be in 'Electronics' or 'Computer Accessories'."
```

### 4. Цена
- Нереалистично низкая цена (возможная ошибка)
- Слишком высокая цена без объяснения
- Несоответствие цены категории
- Возможные десятичные ошибки

**Пример:**
```
❌ Price: $0.50 for wireless mouse
✅ Price: $29.99

AI suggestion: "Price seems unusually low. Did you mean $50.00? 
Typical wireless mice cost $20-60."
```

### 5. Остаток (Stock)
- Товар закончился (stock = 0)
- Критически низкий остаток
- Рекомендации по пополнению

**Пример:**
```
❌ Stock: 0
AI suggestion: "Product is out of stock. Consider marking 
as inactive or adding expected restock date."
```

## 🔧 Как это работает (технически)

### API Endpoint
```
POST /api/cities/[city_id]/products/validate
```

**Request Body:**
```json
{
  "name": "Mous",
  "description": "Small",
  "category": "Food",
  "price": 0.5,
  "stock": 0,
  "sku": "TEST-001"
}
```

**Response:**
```json
[
  {
    "field": "name",
    "issue": "Product name is too short",
    "suggestion": "Add more descriptive details...",
    "confidence": 0.85
  },
  {
    "field": "price",
    "issue": "Price seems unusually low",
    "suggestion": "Verify the price...",
    "confidence": 0.72
  }
]
```

### OpenAI Prompt

Система отправляет следующий промпт в GPT-4o-mini:

```
Analyze this product listing and provide validation feedback:

Product Details:
- Name: Mous
- Description: Small
- Category: Food
- Price: $0.5
- Stock: 0
- SKU: TEST-001

Provide validation feedback as a JSON array with objects containing:
- field: string (name, description, category, price, stock)
- issue: string (if there's a problem, otherwise null)
- suggestion: string (helpful advice)
- confidence: number (0.0 to 1.0)

Focus on:
1. Name - Is it descriptive and professional? Any typos?
2. Description - Is it detailed enough? Missing key information?
3. Category - Does it match the product? Better alternatives?
4. Price - Is it reasonable? Possible pricing errors?
5. Stock - Any concerns about inventory levels?

Return ONLY valid JSON array, no markdown or explanation.
```

### OpenAI Settings

```javascript
{
  model: 'gpt-4o-mini',
  temperature: 0.3,  // Low temperature for consistent, factual responses
  max_tokens: 1000,  // Enough for detailed suggestions
}
```

## 💰 Стоимость

**GPT-4o-mini цены (по состоянию на 2026):**
- Input: ~$0.15 / 1M tokens
- Output: ~$0.60 / 1M tokens

**Примерная стоимость:**
- 1 валидация = ~500 tokens (input + output)
- **~$0.0004 за одну валидацию**
- **1000 валидаций = ~$0.40**

Очень дешево! Можно смело использовать.

## 🚦 Fallback система

Если OpenAI API недоступен или токен неправильный:

1. Система автоматически переключается на **mock валидацию**
2. Использует простые правила (длина текста, диапазоны цен)
3. Пользователь не видит ошибок
4. Валидация всегда работает

**Преимущества:**
- Нет простоев при проблемах с API
- Graceful degradation
- Всегда есть базовая валидация

## 🔐 Настройка токена (для админа)

### Текущая настройка (для тестирования)

Токен уже прописан в `.env.local`:
```bash
OPENAI_API_KEY=sk-proj-ZPMf...
```

### Будущая настройка (в админке)

Планируется добавить в админ-панель:

1. **Settings → AI Configuration**
2. Поле для ввода OpenAI API ключа
3. Кнопка "Test Connection"
4. Toggle для включения/выключения AI
5. Выбор модели (GPT-4o-mini, GPT-4, GPT-3.5-turbo)
6. Настройка temperature и max_tokens

**Безопасность:**
- API ключ хранится зашифрованным в БД
- Никогда не отправляется на клиент
- Используется только на сервере

## 📈 Примеры использования

### Пример 1: Короткое название

**Input:**
```
Name: "KB"
```

**AI Output:**
```json
{
  "field": "name",
  "issue": "Product name is too short and unclear",
  "suggestion": "Expand the name to include brand, product type, and key features. Example: 'Logitech K380 Wireless Bluetooth Keyboard'",
  "confidence": 0.92
}
```

### Пример 2: Неправильная категория

**Input:**
```
Name: "USB-C Charging Cable"
Category: "Electronics"
```

**AI Output:**
```json
{
  "field": "category",
  "issue": null,
  "suggestion": "While 'Electronics' is acceptable, 'Accessories' or 'Cables & Adapters' would be more specific and help with filtering",
  "confidence": 0.78
}
```

### Пример 3: Подозрительная цена

**Input:**
```
Name: "MacBook Pro 16-inch"
Price: $12.99
```

**AI Output:**
```json
{
  "field": "price",
  "issue": "Price is extremely low for this product type",
  "suggestion": "MacBook Pro typically costs $2,000-$3,000. Did you mean $1,299? Please verify this isn't a data entry error.",
  "confidence": 0.95
}
```

### Пример 4: Слабое описание

**Input:**
```
Description: "Good mouse"
```

**AI Output:**
```json
{
  "field": "description",
  "issue": "Description is too vague and lacks detail",
  "suggestion": "Include: connection type (wired/wireless), DPI range, number of buttons, compatibility, battery life, ergonomic features, and ideal use cases (gaming/productivity)",
  "confidence": 0.88
}
```

## 🎯 Настройки confidence (уверенность)

AI возвращает уровень уверенности от 0.0 до 1.0:

- **0.9-1.0** - Очевидная проблема (красный)
- **0.7-0.9** - Серьезная рекомендация (оранжевый)
- **0.5-0.7** - Предложение к улучшению (желтый)
- **0.0-0.5** - Опциональная подсказка (синий)

В UI можно фильтровать по уровню уверенности.

## 🧪 Тестирование

### Тестовые кейсы

**1. Плохой продукт (много ошибок):**
```json
{
  "name": "M",
  "description": "ok",
  "category": "Food",
  "price": 0.1,
  "stock": 0
}
```
Ожидается: 5 предупреждений

**2. Хороший продукт:**
```json
{
  "name": "Logitech MX Master 3S Wireless Mouse",
  "description": "Advanced wireless mouse with 8K DPI sensor, ergonomic design, customizable buttons, and up to 70 days battery life. Perfect for productivity and creative work.",
  "category": "Computer Accessories",
  "price": 99.99,
  "stock": 150
}
```
Ожидается: 0-1 предупреждений

**3. Граничные случаи:**
```json
{
  "name": "",
  "description": null,
  "category": "",
  "price": -10,
  "stock": -5
}
```
Ожидается: Корректная обработка, fallback на mock

## 📱 Интеграция в UI

### В ProductTable

```tsx
// AI включается кнопкой в Toolbar
<button onClick={() => setAiEnabled(!aiEnabled)}>
  🤖 AI {aiEnabled ? 'ON' : 'OFF'}
</button>

// При редактировании ячейки
if (aiEnabled) {
  validateProduct(product); // Вызов API
}

// Показ результатов
{aiValidations[row.id]?.length > 0 && (
  <span className="text-blue-500">🤖</span>
)}
```

### В отдельной странице

```tsx
// Кнопка валидации
<button onClick={testValidation}>
  Validate Product
</button>

// Показ результатов
{validations.map(v => (
  <div>
    {v.issue && <p className="text-red-600">{v.issue}</p>}
    <p className="text-gray-700">{v.suggestion}</p>
    <span>{Math.round(v.confidence * 100)}%</span>
  </div>
))}
```

## 🔍 Мониторинг и логи

### Логирование

Все запросы к OpenAI логируются:

```javascript
console.log('OpenAI validation for product:', product.id);
console.log('Response:', validations);
```

### Обработка ошибок

```javascript
try {
  const validations = await validateWithOpenAI(product);
  return validations;
} catch (error) {
  console.error('OpenAI error:', error);
  // Fallback to mock
  return getMockValidations(product);
}
```

### Метрики (будущее)

- Количество валидаций в день
- Средний confidence score
- Частота использования fallback
- Топ проблемных полей
- Время ответа API

## 📚 Документация API

### Структура ответа

```typescript
interface AIValidation {
  field: 'name' | 'description' | 'category' | 'price' | 'stock';
  issue?: string;      // null если нет проблемы
  suggestion: string;  // Всегда есть
  confidence: number;  // 0.0 - 1.0
}
```

### HTTP статусы

- **200** - Успешная валидация
- **500** - Ошибка (возвращает mock валидацию)

### Rate Limiting

OpenAI имеет лимиты:
- **500 requests/min** (Tier 1)
- **10,000 requests/min** (Tier 2+)

Рекомендуется:
- Debounce по 1-2 секунды
- Кэширование результатов
- Батчинг запросов

## 🎓 Советы по использованию

### Для пользователей

1. **Включайте AI** только когда нужны подробные проверки
2. **Не игнорируйте** высокий confidence (>0.8)
3. **Используйте как подсказки**, не как строгие правила
4. **Проверяйте логику** - AI может ошибаться

### Для разработчиков

1. **Настройте temperature** - меньше = точнее, больше = креативнее
2. **Кэшируйте** результаты для одинаковых продуктов
3. **Мониторьте токены** - добавьте счетчик использования
4. **A/B тестируйте** разные промпты
5. **Добавьте feedback** - кнопки "Полезно" / "Не полезно"

## 🚀 Готово к использованию!

1. **Запустите сервер**: `npm run dev`
2. **Откройте тест**: http://localhost:3000/test-ai
3. **Или таблицу**: http://localhost:3000/products
4. **Включите AI** и тестируйте!

Токен уже настроен, все работает из коробки! 🎉
