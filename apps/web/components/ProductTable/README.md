# ProductTable Component

A Google Sheets-like product catalog editor with AI validation and comprehensive audit logging.

## 🎯 Features

### 📊 Spreadsheet UI
- **Editable cells**: Click any cell to edit (except ID and timestamp columns)
- **Keyboard navigation**: Tab, Arrow keys, Enter for efficient navigation
- **Multi-select**: Shift+Click for range selection, Ctrl+Click for individual selection
- **Column sorting**: Click column headers to sort (ASC → DESC → NONE)
- **Column resizing**: Drag column borders to resize
- **Search**: Real-time search across all fields

### ⚙️ Operations
- **Add row**: Create new blank products
- **Delete row**: Delete selected products with confirmation
- **Bulk edit**: Update a single field across multiple selected products
- **Import CSV**: Upload CSV files to bulk import products
- **Export CSV**: Download current view as CSV
- **Undo/Redo**: Local history of last 10 actions (Ctrl+Z / Ctrl+Y)

### 🤖 AI Validation (Powered by OpenAI GPT-4o-mini)
- Toggle AI validation on/off
- **Real-time OpenAI integration** - Uses GPT-4o-mini for smart analysis
- Checks product names for typos and clarity
- Validates price ranges and detects errors
- Assesses description completeness
- Suggests better categories
- Shows AI suggestions with confidence scores
- **Automatic fallback** to rule-based validation if API unavailable
- **Cost:** ~$0.0004 per validation (very affordable)

### 📜 Audit Trail
- Logs every cell edit
- Shows who changed what and when
- Diff view (old value → new value)
- Per-product history panel

### 💾 Real-time Sync
- Auto-saves edits 1 second after typing stops
- Optimistic updates (instant UI feedback)
- Rollback on server errors
- Success/error toast notifications

## 🚀 Quick Start

```bash
# Navigate to web app
cd apps/web

# Install dependencies (already done)
npm install

# Start development server
npm run dev

# Open browser
# http://localhost:3000/products
```

## 💻 Usage

```tsx
import ProductTable from '@/components/ProductTable';

export default function ProductsPage() {
  return (
    <ProductTable 
      cityId="city-123" 
      currentUser="user@example.com" 
    />
  );
}
```

## 📋 Props

| Prop | Type | Description |
|------|------|-------------|
| `cityId` | `string` | City ID for API endpoints |
| `currentUser` | `string` | Current user identifier for audit logs |

## 🏗️ File Structure

```
ProductTable/
├── ProductTable.tsx        # Main component (420 lines)
├── Toolbar.tsx            # Top toolbar with actions (140 lines)
├── AuditPanel.tsx         # Sidebar audit history (110 lines)
├── AIValidationBadge.tsx  # AI suggestion popover (50 lines)
├── api.ts                 # API client functions (60 lines)
├── types.ts               # TypeScript interfaces (50 lines)
├── utils.ts               # Utility functions (85 lines)
├── useHistory.ts          # Undo/redo hook (45 lines)
└── index.ts               # Exports
```

## 🔌 API Endpoints

The component expects these Next.js API routes (all included):

```
/api/cities/[city_id]/products              # GET, POST
/api/cities/[city_id]/products/[id]         # PUT, DELETE
/api/cities/[city_id]/products/[id]/audit-logs  # GET
/api/cities/[city_id]/products/bulk         # POST
/api/cities/[city_id]/products/validate     # POST
```

## ⌨️ Keyboard Shortcuts

- **Ctrl+Z**: Undo last action
- **Ctrl+Y** or **Ctrl+Shift+Z**: Redo
- **Tab**: Navigate to next cell
- **Shift+Tab**: Navigate to previous cell
- **Arrow keys**: Navigate cells
- **Enter**: Edit selected cell
- **Escape**: Cancel edit

## 🎨 Styling

Built with Tailwind CSS. All styles are utility-based and can be customized in `tailwind.config.ts`.

## 📦 Dependencies

- `react-data-grid` (^7.0.0) - Spreadsheet grid component
- `react-hot-toast` (^2.4.1) - Toast notifications
- `papaparse` (^5.4.1) - CSV parsing and generation
- `@types/papaparse` (^5.3.8) - TypeScript types
- `openai` (^4.20.0) - AI validation API client

## 🧪 Testing

1. **Basic editing**: Click any cell, type, press Tab
2. **Multi-select**: Shift+Click to select range
3. **Delete**: Select rows, click Delete button
4. **Import CSV**: Click Import CSV, select a CSV file
5. **Export CSV**: Click Export CSV
6. **AI validation**: Toggle AI ON, edit a product with short name
7. **Audit history**: Click "History" button on any row
8. **Undo/Redo**: Make changes, press Ctrl+Z to undo

## 🔐 Security Notes

⚠️ **Current implementation uses mock data for demonstration**

For production:
- Add authentication middleware
- Validate user permissions per city
- Sanitize all inputs (XSS prevention)
- Rate limit API endpoints
- Use parameterized database queries
- Implement audit log immutability

## 🚧 Known Limitations

1. **No virtual scrolling**: Performance degrades with 10,000+ products
2. **Undo/redo limited**: Only tracks edit operations
3. **Bulk edit UX**: Uses browser prompts (should be modal)
4. **AI validation**: Mock logic (needs real LLM integration)
5. **WebSocket**: Not implemented (manual refresh for multi-user)

## 🎯 Future Enhancements

- Virtual scrolling (react-window) for large datasets
- WebSocket support for real-time collaboration
- Better bulk edit modal with form validation
- Column visibility toggles
- Advanced filters (price range, category dropdown)
- Drag & drop row reordering
- Export to Excel (.xlsx)
- Conditional formatting
- Dark mode support

## 📚 Learn More

- [react-data-grid docs](https://react-data-grid.js.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Next.js API Routes](https://nextjs.org/docs/api-routes/introduction)

## 📄 License

Part of the zeta-platform project.
